"""终端实操题判分器：在工作目录副本内运行 check.py（cwd=判分副本，退出码 0 即通过）。"""

import shutil
import subprocess
import sys
from pathlib import Path

from litmus.diffcheck import find_symlinks
from litmus.graders import GradeResult
from litmus.graders.code import _copy_clean_tree
from litmus.tasks import TaskSpec


def grade_terminal(
    task: TaskSpec, workdir: Path, grade_dir: Path, bundle_dir: Path
) -> GradeResult:
    symlinks = find_symlinks(workdir)
    if symlinks:
        return GradeResult(
            passed=False,
            reasons=["工作目录存在不允许的符号链接: {}".format(", ".join(symlinks))],
            merge_veto=False,
            extra={},
        )

    check_script = Path(bundle_dir) / "check.py"
    if not check_script.is_file():
        return GradeResult(
            passed=False,
            reasons=["判分包缺少 check.py"],
            merge_veto=False,
            extra={},
        )

    eval_dir = Path(grade_dir) / "eval"
    try:
        _copy_clean_tree(workdir, eval_dir)
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-B", str(check_script.resolve())],
                cwd=str(eval_dir),
                capture_output=True,
                text=True,
                timeout=60.0,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return GradeResult(
                passed=False,
                reasons=["终端检查脚本执行超时 (60s)"],
                merge_veto=False,
                extra={},
            )

        if proc.returncode == 0:
            return GradeResult(passed=True, reasons=[], merge_veto=False, extra={})
        msg = (proc.stderr or proc.stdout).strip()
        reason = "检查脚本返回非零退出码 ({})".format(proc.returncode)
        if msg:
            reason = "{}: {}".format(reason, msg[:500])
        return GradeResult(passed=False, reasons=[reason], merge_veto=False, extra={})
    finally:
        shutil.rmtree(str(eval_dir), ignore_errors=True)
