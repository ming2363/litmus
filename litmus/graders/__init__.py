"""判分器统一入口与 GradeResult 数据结构。"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from litmus.tasks import TaskSpec


@dataclass
class GradeResult:
    passed: bool
    reasons: List[str]
    merge_veto: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)


def grade(
    task: TaskSpec, workdir: Path, grade_dir: Path, bundle_dir: Path
) -> GradeResult:
    """按 task.grader 分发到对应判分器。"""
    if task.grader == "tests":
        from litmus.graders.code import grade_code

        return grade_code(task, workdir, grade_dir, bundle_dir)
    if task.grader == "terminal":
        from litmus.graders.terminal import grade_terminal

        return grade_terminal(task, workdir, grade_dir, bundle_dir)
    if task.grader == "tool_call":
        from litmus.graders.tool_call import grade_tool_call

        return grade_tool_call(task, workdir, grade_dir, bundle_dir)
    if task.grader == "read_code":
        from litmus.graders.read_code import grade_read_code

        return grade_read_code(task, workdir, grade_dir, bundle_dir)
    if task.grader == "review":
        from litmus.graders.review import grade_review

        return grade_review(task, workdir, grade_dir, bundle_dir)
    raise ValueError("未知判分器类型: {}".format(task.grader))
