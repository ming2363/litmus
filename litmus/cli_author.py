"""出题管理端命令行实现：seal / unseal / selftest / lint。"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from litmus.crypto import CryptoError, seal_dir, unseal_to
from litmus.graders import grade
from litmus.graders.code import _copy_clean_tree, _overlay_tree, evaluate_tests_in_dir
from litmus.integrity import append_audit, find_forbidden_files
from litmus.paths import answers_dir, find_repo_root
from litmus.state import has_active_run
from litmus.tasks import TaskSpec, TaskValidationError, load_all_tasks, load_task
from litmus.testexec import CompileError, TestTimeoutError


def _cmd_seal(args: argparse.Namespace, root: Path) -> int:
    adir = answers_dir(root)
    if not adir.is_dir():
        print("answers/ 目录不存在: {}".format(adir))
        return 1

    if args.all:
        targets = sorted(p.name for p in adir.iterdir() if p.is_dir() and not p.name.startswith("."))
        if not targets:
            print("answers/ 下没有待加密的明文目录")
            return 0
    elif args.task_id:
        targets = [args.task_id]
    else:
        print("请指定题号或使用 --all")
        return 1

    for tid in targets:
        plain_dir = adir / tid
        grade_src = plain_dir / "grade"
        sol_src = plain_dir / "solution"
        if not grade_src.is_dir() or not sol_src.is_dir():
            print("题目 {} 缺少明文 grade/ 或 solution/ 目录: {}".format(tid, plain_dir))
            return 1

        append_audit("seal", task_id=tid, run_dir=None, root=root)
        seal_dir(grade_src, adir / "{}.grade.enc".format(tid))
        seal_dir(sol_src, adir / "{}.solution.enc".format(tid))
        shutil.rmtree(str(plain_dir))
        print("已加密并清理明文目录: {}".format(tid))
    return 0


def _cmd_unseal(task_id: str, root: Path) -> int:
    active_run = has_active_run(root)
    if active_run is not None:
        print("存在未完成的测评 ({})，禁止执行 unseal".format(active_run))
        return 1

    adir = answers_dir(root)
    grade_enc = adir / "{}.grade.enc".format(task_id)
    sol_enc = adir / "{}.solution.enc".format(task_id)
    if not grade_enc.is_file() or not sol_enc.is_file():
        print("题目 {} 缺少密文文件 (.grade.enc / .solution.enc)".format(task_id))
        return 1

    append_audit("unseal", task_id=task_id, run_dir=None, root=root)
    dest_dir = adir / task_id
    unseal_to(grade_enc, dest_dir / "grade")
    unseal_to(sol_enc, dest_dir / "solution")
    print("已解密到: {}".format(dest_dir))
    return 0


def _selftest_one(task: TaskSpec, root: Path) -> Tuple[bool, str]:
    adir = answers_dir(root)
    grade_enc = adir / "{}.grade.enc".format(task.id)
    sol_enc = adir / "{}.solution.enc".format(task.id)
    if not grade_enc.is_file() or not sol_enc.is_file():
        return False, "缺少 .grade.enc 或 .solution.enc（请先 seal）"

    append_audit("selftest", task_id=task.id, run_dir=None, root=root)
    with tempfile.TemporaryDirectory(prefix="litmus_selftest_") as tmp_str:
        tmp = Path(tmp_str)
        bundle_dir = tmp / "grade_bundle"
        sol_dir = tmp / "solution_bundle"
        try:
            unseal_to(grade_enc, bundle_dir)
            unseal_to(sol_enc, sol_dir)
        except CryptoError as exc:
            return False, "解密失败: {}".format(exc)

        # 阶段 1：起始状态必须不通过（连续跑 3 次校验稳定性）
        init_signatures: List[Tuple] = []
        for run_idx in range(3):
            if task.grader == "tests":
                try:
                    outcomes, f2p, p2p = evaluate_tests_in_dir(task, task.repo_dir, bundle_dir)
                except (CompileError, TestTimeoutError) as exc:
                    return False, "起始代码执行测试异常 (第 {} 次): {}".format(run_idx + 1, exc)

                bad_f2p = [tid for tid in f2p if tid not in outcomes or outcomes[tid].status == "pass"]
                bad_p2p = [tid for tid in p2p if tid not in outcomes or outcomes[tid].status != "pass"]
                if bad_f2p:
                    return False, "起始状态下部分 F2P 用例意外通过或缺失: {}".format(", ".join(bad_f2p))
                if bad_p2p:
                    return False, "起始状态下部分 P2P 用例未通过: {}".format(", ".join(bad_p2p))
                sig = tuple((tid, outcomes[tid].status) for tid in sorted(outcomes.keys()))
                init_signatures.append(sig)
            else:
                work_init = tmp / "init_work_{}".format(run_idx)
                g_init = tmp / "init_grade_{}".format(run_idx)
                _copy_clean_tree(task.repo_dir, work_init)
                if task.answer_file and (work_init / task.answer_file).exists():
                    (work_init / task.answer_file).unlink()
                res = grade(task, work_init, g_init, bundle_dir)
                if res.passed:
                    return False, "起始状态（空答案/初始目录）意外判通过"
                init_signatures.append((res.passed,))

        if len(set(init_signatures)) != 1:
            return False, "起始状态连续 3 次运行结果不一致"

        # 阶段 2：套用参考解后必须通过（连续跑 3 次校验稳定性）
        sol_signatures: List[Tuple] = []
        for run_idx in range(3):
            work_sol = tmp / "sol_work_{}".format(run_idx)
            g_sol = tmp / "sol_grade_{}".format(run_idx)
            _copy_clean_tree(task.repo_dir, work_sol)
            _overlay_tree(sol_dir, work_sol)

            res = grade(task, work_sol, g_sol, bundle_dir)
            if not res.passed:
                return False, "参考解第 {} 次判分未通过: {}".format(run_idx + 1, "; ".join(res.reasons))

            if task.grader == "tests":
                outcomes, _, _ = evaluate_tests_in_dir(task, work_sol, bundle_dir)
                sig = tuple((tid, outcomes[tid].status) for tid in sorted(outcomes.keys()))
                sol_signatures.append(sig)
            else:
                sol_signatures.append((res.passed,))

        if len(set(sol_signatures)) != 1:
            return False, "参考解连续 3 次运行结果不一致"

    return True, "起始/参考解各 3 次验证通过且结果一致"


def _cmd_selftest(task_id: Optional[str], root: Path) -> int:
    active_run = has_active_run(root)
    if active_run is not None:
        print("存在未完成的测评 ({})，禁止执行 selftest".format(active_run))
        return 1

    if task_id:
        targets = [load_task(task_id, root)]
    else:
        manifest, tasks = load_all_tasks(root)
        targets = [tasks[tid] for tid in manifest.order]

    all_ok = True
    for task in targets:
        ok, detail = _selftest_one(task, root)
        tag = "PASS" if ok else "FAIL"
        print("[{}] {}: {}".format(tag, task.id, detail))
        if not ok:
            all_ok = False
    return 0 if all_ok else 1


def _cmd_lint(root: Path) -> int:
    errors: List[str] = []

    forbidden = find_forbidden_files(root)
    if forbidden:
        errors.append("发现禁止文件: {}".format(", ".join(forbidden)))

    tasks: Dict[str, TaskSpec] = {}
    try:
        manifest, tasks = load_all_tasks(root)
    except TaskValidationError as exc:
        errors.append("题目结构或 manifest 校验失败: {}".format(exc))
        manifest = None

    if manifest is not None:
        adir = answers_dir(root)
        for tid in manifest.order:
            has_enc = (adir / "{}.grade.enc".format(tid)).is_file() and (
                adir / "{}.solution.enc".format(tid)
            ).is_file()
            has_plain = (adir / tid / "grade").is_dir() and (adir / tid / "solution").is_dir()
            if not has_enc and not has_plain:
                errors.append("题目 {} 缺少答案文件（既无加密包也无明文目录）".format(tid))

    if errors:
        print("lint 检查未通过：")
        for e in errors:
            print("- {}".format(e))
        return 1

    print("lint 检查通过：共 {} 道题目，无禁止文件，manifest 与题目目录一致。".format(len(tasks)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="author.py",
        description="litmus 出题管理与校验工具",
    )
    sub = parser.add_subparsers(dest="command")

    p_seal = sub.add_parser("seal", help="加密答案目录并删除明文")
    p_seal.add_argument("task_id", nargs="?", help="题号")
    p_seal.add_argument("--all", action="store_true", help="加密 answers/ 下全部明文目录")

    p_unseal = sub.add_parser("unseal", help="解密题目答案用于修改")
    p_unseal.add_argument("task_id", help="题号")

    p_selftest = sub.add_parser("selftest", help="自动自检题目（起始失败/参考解通过各跑 3 次）")
    p_selftest.add_argument("task_id", nargs="?", default=None, help="可选，仅自检指定题号")

    sub.add_parser("lint", help="检查禁止文件、manifest 与题目目录一致性")
    return parser


def main(argv: Optional[List[str]] = None, root: Optional[Path] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = root if root is not None else find_repo_root()

    if args.command == "seal":
        return _cmd_seal(args, repo_root)
    if args.command == "unseal":
        return _cmd_unseal(args.task_id, repo_root)
    if args.command == "selftest":
        return _cmd_selftest(args.task_id, repo_root)
    if args.command == "lint":
        return _cmd_lint(repo_root)

    parser.print_help()
    return 0
