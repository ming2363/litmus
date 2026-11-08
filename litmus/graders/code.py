"""代码类判分器（修 Bug、新功能、小范围编辑）：可合入性检查 + 覆盖隐藏测试 + F2P/P2P 判定。"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

from litmus.diffcheck import (
    DiffError,
    check_allowed_paths,
    compare_dirs,
    is_visible_test_file,
)
from litmus.graders import GradeResult
from litmus.paths import is_ignored_relpath
from litmus.tasks import TaskSpec
from litmus.testexec import CompileError, TestOutcome, TestTimeoutError, compile_project, run_tests


def _copy_clean_tree(src: Path, dst: Path) -> None:
    """复制工作目录到判分沙箱，跳过构建产物与忽略文件。"""
    src_root = Path(src)
    dst_root = Path(dst)
    if dst_root.exists():
        shutil.rmtree(str(dst_root))
    dst_root.mkdir(parents=True, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(str(src_root), followlinks=False):
        cur = Path(dirpath)
        kept_dirs: List[str] = []
        for dname in sorted(dirnames):
            rel_dir = (cur / dname).relative_to(src_root).as_posix() + "/x"
            if not is_ignored_relpath(rel_dir):
                kept_dirs.append(dname)
                (dst_root / (cur / dname).relative_to(src_root)).mkdir(parents=True, exist_ok=True)
        dirnames[:] = kept_dirs
        for fname in sorted(filenames):
            fpath = cur / fname
            rel = fpath.relative_to(src_root).as_posix()
            if is_ignored_relpath(rel):
                continue
            target = dst_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(fpath), str(target))


def _overlay_tree(src: Path, dst: Path) -> None:
    """将 src 目录内容按相对路径覆盖到 dst 根目录下。"""
    src_root = Path(src)
    dst_root = Path(dst)
    if not src_root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(str(src_root), followlinks=False):
        cur = Path(dirpath)
        dirnames.sort()
        for fname in sorted(filenames):
            fpath = cur / fname
            rel = fpath.relative_to(src_root)
            target = dst_root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(fpath), str(target))


def _load_grade_meta(bundle_dir: Path) -> Tuple[List[str], List[str], Dict[str, float]]:
    meta_path = Path(bundle_dir) / "meta.json"
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    f2p = [str(x) for x in data.get("f2p", [])]
    p2p = [str(x) for x in data.get("p2p", [])]
    timeouts: Dict[str, float] = {}
    raw_to = data.get("timeouts", {})
    if isinstance(raw_to, dict):
        for k, v in raw_to.items():
            timeouts[str(k)] = float(v)
    return f2p, p2p, timeouts


def evaluate_tests_in_dir(
    task: TaskSpec, target_dir: Path, bundle_dir: Path
) -> Tuple[Dict[str, TestOutcome], List[str], List[str]]:
    """在临时副本上叠加隐藏测试并执行全部 F2P/P2P 用例（供 selftest 逐项验证）。"""
    f2p, p2p, timeouts = _load_grade_meta(bundle_dir)
    all_ids = f2p + p2p
    with tempfile.TemporaryDirectory(prefix="litmus_eval_") as tmp:
        eval_dir = Path(tmp) / "eval"
        _copy_clean_tree(target_dir, eval_dir)
        _overlay_tree(Path(bundle_dir) / "tests", eval_dir)
        outcomes = run_tests(task.lang, eval_dir, test_ids=all_ids, timeouts=timeouts)
    return outcomes, f2p, p2p


def grade_code(
    task: TaskSpec, workdir: Path, grade_dir: Path, bundle_dir: Path
) -> GradeResult:
    """执行设计 5.2 全流程判分。"""
    grade_root = Path(grade_dir)
    eval_dir = grade_root / "eval"
    extra: Dict[str, Any] = {}

    try:
        # 1. 可合入性检查：先对比差异与符号链接，再复制并校验编译
        veto_reasons: List[str] = []
        try:
            diff = compare_dirs(task.repo_dir, workdir)
            extra["changed_files"] = diff.changed_files
            extra["changed_lines"] = diff.changed_lines

            path_violations = check_allowed_paths(diff.changed_files, task.allowed_paths)
            if path_violations:
                veto_reasons.append("修改了允许范围外的文件: {}".format(", ".join(path_violations)))

            touched_visible = [
                rel for rel in (diff.modified + diff.deleted) if is_visible_test_file(rel)
            ]
            if touched_visible:
                veto_reasons.append("可见测试文件被修改或删除: {}".format(", ".join(sorted(touched_visible))))

            if task.max_changed_lines is not None and diff.changed_lines > task.max_changed_lines:
                veto_reasons.append(
                    "改动行数 {} 超过上限 {}".format(diff.changed_lines, task.max_changed_lines)
                )
        except DiffError as exc:
            veto_reasons.append(str(exc))

        if not veto_reasons:
            _copy_clean_tree(workdir, eval_dir)
            try:
                compile_project(task.lang, eval_dir)
            except CompileError as exc:
                veto_reasons.append("代码编译失败: {}".format(exc))

        if veto_reasons:
            return GradeResult(
                passed=False,
                reasons=veto_reasons,
                merge_veto=True,
                extra=extra,
            )

        # 2. 覆盖隐藏测试
        f2p, p2p, timeouts = _load_grade_meta(bundle_dir)
        all_ids = f2p + p2p
        _overlay_tree(Path(bundle_dir) / "tests", eval_dir)

        # 3. 运行内置测试运行器
        try:
            outcomes = run_tests(
                task.lang,
                eval_dir,
                test_ids=all_ids,
                timeouts=timeouts,
            )
        except (CompileError, TestTimeoutError) as exc:
            return GradeResult(
                passed=False,
                reasons=[str(exc)],
                merge_veto=False,
                extra=extra,
            )

        # 4. F2P / P2P 判定
        reasons: List[str] = []
        f2p_passed = 0
        for tid in f2p:
            out = outcomes.get(tid)
            if out is None:
                reasons.append("F2P 用例未产生结果: {}".format(tid))
            elif out.status != "pass":
                reasons.append("F2P 未通过 ({}): {} - {}".format(tid, out.status, out.message))
            else:
                f2p_passed += 1

        p2p_passed = 0
        for tid in p2p:
            out = outcomes.get(tid)
            if out is None:
                reasons.append("P2P 用例未产生结果: {}".format(tid))
            elif out.status != "pass":
                reasons.append("P2P 回归失败 ({}): {} - {}".format(tid, out.status, out.message))
            else:
                p2p_passed += 1

        extra["f2p_passed"] = f2p_passed
        extra["f2p_total"] = len(f2p)
        extra["p2p_passed"] = p2p_passed
        extra["p2p_total"] = len(p2p)

        passed = len(all_ids) > 0 and len(reasons) == 0
        if not all_ids:
            reasons.append("meta.json 未定义任何测试用例")
        return GradeResult(
            passed=passed,
            reasons=reasons,
            merge_veto=False,
            extra=extra,
        )
    finally:
        shutil.rmtree(str(eval_dir), ignore_errors=True)
