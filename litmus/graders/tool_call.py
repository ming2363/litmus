"""工具调用判分器：支持有序/无序、参数归一化、空列表与多余参数严格拒绝。"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from litmus.graders import GradeResult
from litmus.tasks import TaskSpec

_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%Y.%m.%d",
    "%Y-%m-%dT%H:%M:%S",
    "%b %d, %Y",
    "%B %d, %Y",
)


def _normalize_date(raw: str) -> str:
    text = raw.strip()
    m = re.match(r"^(\d{4})年(\d{1,2})月(\d{1,2})日$", text)
    if m:
        return "{:04d}-{:02d}-{:02d}".format(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text


def _apply_rules(val: Any, rules: Sequence[str]) -> Any:
    if isinstance(val, list):
        return [_apply_rules(x, rules) for x in val]
    if isinstance(val, dict):
        return {k: _apply_rules(v, rules) for k, v in val.items()}
    if not isinstance(val, str):
        return val
    out = val
    for rule in rules:
        if rule == "strip":
            out = out.strip()
        elif rule == "lower":
            out = out.lower()
        elif rule == "date":
            out = _normalize_date(out)
    return out


def _strict_equal(a: Any, b: Any) -> bool:
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(_strict_equal(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        return all(_strict_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    return type(a) is type(b) and a == b


def _call_matches(
    actual: Dict[str, Any],
    expected: Dict[str, Any],
    norm_rules: Dict[str, List[str]],
) -> Optional[str]:
    if actual.get("name") != expected.get("name"):
        return "函数名不匹配: {} != {}".format(actual.get("name"), expected.get("name"))

    act_args = actual.get("args", {})
    exp_args = expected.get("args", {})
    if not isinstance(act_args, dict):
        return "args 必须是对象"

    extra_keys = sorted(set(act_args.keys()) - set(exp_args.keys()))
    if extra_keys:
        return "出现未定义的多余参数: {}".format(", ".join(extra_keys))

    missing_keys = sorted(set(exp_args.keys()) - set(act_args.keys()))
    if missing_keys:
        return "缺少必填参数: {}".format(", ".join(missing_keys))

    for k, exp_v in exp_args.items():
        rules = norm_rules.get(k, [])
        norm_act = _apply_rules(act_args[k], rules)
        norm_exp = _apply_rules(exp_v, rules)
        if not _strict_equal(norm_act, norm_exp):
            return "参数 {} 值不匹配: {} != {}".format(k, norm_act, norm_exp)
    return None


def _unordered_match(
    actual_calls: List[Dict[str, Any]],
    expected_calls: List[Dict[str, Any]],
    norm_rules: Dict[str, List[str]],
) -> bool:
    n = len(expected_calls)
    adj: List[List[int]] = []
    for exp_call in expected_calls:
        adj.append([
            j for j, act_call in enumerate(actual_calls)
            if _call_matches(act_call, exp_call, norm_rules) is None
        ])

    match_act_to_exp: List[int] = [-1] * n

    def _dfs(exp_idx: int, seen: List[bool]) -> bool:
        for act_idx in adj[exp_idx]:
            if seen[act_idx]:
                continue
            seen[act_idx] = True
            if match_act_to_exp[act_idx] == -1 or _dfs(match_act_to_exp[act_idx], seen):
                match_act_to_exp[act_idx] = exp_idx
                return True
        return False

    for i in range(n):
        if not _dfs(i, [False] * n):
            return False
    return True


def grade_tool_call(
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

    if not isinstance(actual, list):
        return GradeResult(passed=False, reasons=["tool_call 答案必须是 JSON 数组"])

    for idx, item in enumerate(actual):
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            return GradeResult(passed=False, reasons=["第 {} 条调用缺少字符串字段 name".format(idx + 1)])
        if "args" in item and not isinstance(item["args"], dict):
            return GradeResult(passed=False, reasons=["第 {} 条调用的 args 必须是对象".format(idx + 1)])

    expected = json.loads((Path(bundle_dir) / "expected.json").read_text(encoding="utf-8"))
    ordered = bool(expected.get("ordered", True))
    expected_calls = expected.get("calls", [])
    norm_rules = expected.get("normalize", {})

    if len(actual) != len(expected_calls):
        return GradeResult(
            passed=False,
            reasons=["调用次数不匹配: 期望 {} 次，实际 {} 次".format(len(expected_calls), len(actual))],
        )

    if ordered:
        for idx, (act_call, exp_call) in enumerate(zip(actual, expected_calls)):
            err = _call_matches(act_call, exp_call, norm_rules)
            if err is not None:
                return GradeResult(passed=False, reasons=["第 {} 次调用不匹配: {}".format(idx + 1, err)])
        return GradeResult(passed=True, reasons=[])

    if _unordered_match(actual, expected_calls, norm_rules):
        return GradeResult(passed=True, reasons=[])
    return GradeResult(passed=False, reasons=["无序工具调用集合未能与预期一一配对"])
