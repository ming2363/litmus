"""读代码题判分器：归一化字符串后对任意 JSON 结构做严格等价比较。"""

import json
from pathlib import Path
from typing import Any, Sequence

from litmus.graders import GradeResult
from litmus.graders.tool_call import _strict_equal
from litmus.tasks import TaskSpec


def _normalize_value(val: Any, rules: Sequence[str]) -> Any:
    if isinstance(val, str):
        out = val
        for rule in rules:
            if rule == "strip":
                out = out.strip()
            elif rule == "lower":
                out = out.lower()
        return out
    if isinstance(val, list):
        return [_normalize_value(x, rules) for x in val]
    if isinstance(val, dict):
        return {k: _normalize_value(v, rules) for k, v in val.items()}
    return val


def grade_read_code(
    task: TaskSpec, workdir: Path, grade_dir: Path, bundle_dir: Path
) -> GradeResult:
    answer_name = task.answer_file or "answer.json"
    ans_path = Path(workdir) / answer_name
    if ans_path.is_symlink() or not ans_path.is_file():
        return GradeResult(passed=False, reasons=["缺少答案文件: {}".format(answer_name)])

    try:
        actual = json.loads(ans_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return GradeResult(passed=False, reasons=["答案 JSON 不合法: {}".format(exc)])

    expected_obj = json.loads((Path(bundle_dir) / "expected.json").read_text(encoding="utf-8"))
    rules = expected_obj.get("normalize", [])
    expected_ans = expected_obj.get("answer")

    norm_actual = _normalize_value(actual, rules)
    norm_expected = _normalize_value(expected_ans, rules)
    if _strict_equal(norm_actual, norm_expected):
        return GradeResult(passed=True, reasons=[])
    return GradeResult(passed=False, reasons=["读代码答案与标准答案不一致"])
