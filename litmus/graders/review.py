"""Code Review 判分器：类别+行号容差精确最优一一配对，限制最大条数并统计额外条目数。"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from litmus.graders import GradeResult
from litmus.paths import strip_rel_prefix
from litmus.tasks import TaskSpec


def _norm_rel_path(p: str) -> str:
    # 不能用 lstrip("./")：它按字符剥离，会把 ../x 收成 x、把 .env 收成 env
    return strip_rel_prefix(p.strip())


def _optimal_group_match(
    sub_lines: List[int],
    exp_lines: List[int],
    tolerance: int,
) -> Tuple[int, int]:
    """在同 (file, category) 组内求最大匹配数及最小总行距（每组最多 <=10 条，精确搜索）。"""
    m = len(sub_lines)
    n = len(exp_lines)
    edges: List[List[Tuple[int, int]]] = []
    for i in range(m):
        cand = []
        for j in range(n):
            dist = abs(sub_lines[i] - exp_lines[j])
            if dist <= tolerance:
                cand.append((j, dist))
        edges.append(cand)

    best_count = 0
    best_dist = 0
    used_exp = [False] * n

    def _dfs(idx: int, cur_count: int, cur_dist: int) -> None:
        nonlocal best_count, best_dist
        if cur_count + (m - idx) < best_count:
            return
        if idx == m:
            if cur_count > best_count or (cur_count == best_count and cur_dist < best_dist):
                best_count = cur_count
                best_dist = cur_dist
            return
        for j, dist in edges[idx]:
            if not used_exp[j]:
                used_exp[j] = True
                _dfs(idx + 1, cur_count + 1, cur_dist + dist)
                used_exp[j] = False
        _dfs(idx + 1, cur_count, cur_dist)

    _dfs(0, 0, 0)
    return best_count, best_dist


def grade_review(
    task: TaskSpec, workdir: Path, grade_dir: Path, bundle_dir: Path
) -> GradeResult:
    answer_name = task.answer_file or "review.json"
    ans_path = Path(workdir) / answer_name
    if ans_path.is_symlink() or not ans_path.is_file():
        return GradeResult(
            passed=False,
            reasons=["缺少审查文件: {}".format(answer_name)],
            extra={"extra_items": 0},
        )

    try:
        items = json.loads(ans_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return GradeResult(
            passed=False,
            reasons=["审查 JSON 不合法: {}".format(exc)],
            extra={"extra_items": 0},
        )

    if not isinstance(items, list):
        return GradeResult(
            passed=False,
            reasons=["review.json 必须是 JSON 数组"],
            extra={"extra_items": 0},
        )

    expected_obj = json.loads((Path(bundle_dir) / "expected.json").read_text(encoding="utf-8"))
    expected_issues = expected_obj.get("issues", [])
    max_items = int(expected_obj.get("max_items", 10))
    tolerance = int(expected_obj.get("line_tolerance", 3))
    allowed_categories = expected_obj.get("categories")

    if len(items) > max_items:
        return GradeResult(
            passed=False,
            reasons=["审查条目数 {} 超过上限 {}".format(len(items), max_items)],
            extra={"extra_items": max(0, len(items) - len(expected_issues)), "matched": 0, "expected": len(expected_issues)},
        )

    sub_groups: Dict[Tuple[str, str], List[int]] = defaultdict(list)
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            return GradeResult(
                passed=False,
                reasons=["第 {} 条审查意见不是 JSON 对象".format(idx + 1)],
                extra={"extra_items": 0},
            )
        f = item.get("file")
        line = item.get("line")
        cat = item.get("category")
        if not isinstance(f, str) or not f.strip():
            return GradeResult(
                passed=False,
                reasons=["第 {} 条审查意见缺少合法 file".format(idx + 1)],
                extra={"extra_items": 0},
            )
        if isinstance(line, bool) or not isinstance(line, int) or line < 1:
            return GradeResult(
                passed=False,
                reasons=["第 {} 条审查意见缺少正整数 line".format(idx + 1)],
                extra={"extra_items": 0},
            )
        if not isinstance(cat, str) or not cat.strip():
            return GradeResult(
                passed=False,
                reasons=["第 {} 条审查意见缺少合法 category".format(idx + 1)],
                extra={"extra_items": 0},
            )
        if isinstance(allowed_categories, list) and cat.strip() not in allowed_categories:
            return GradeResult(
                passed=False,
                reasons=["第 {} 条审查意见使用了不在列表中的类别: {}".format(idx + 1, cat)],
                extra={"extra_items": 0},
            )
        sub_groups[(_norm_rel_path(f), cat.strip().lower())].append(line)

    exp_groups: Dict[Tuple[str, str], List[int]] = defaultdict(list)
    for issue in expected_issues:
        exp_groups[(_norm_rel_path(issue["file"]), issue["category"].strip().lower())].append(
            int(issue["line"])
        )

    total_matched = 0
    unmatched_reasons: List[str] = []
    for key, exp_lines in exp_groups.items():
        sub_lines = sub_groups.get(key, [])
        matched_cnt, _ = _optimal_group_match(sub_lines, exp_lines, tolerance)
        total_matched += matched_cnt
        if matched_cnt < len(exp_lines):
            unmatched_reasons.append(
                "预埋问题未全部命中 ({} / {}): 期望 {} 个，命中 {} 个".format(
                    key[0], key[1], len(exp_lines), matched_cnt
                )
            )

    extra_items = len(items) - total_matched
    passed = len(expected_issues) > 0 and total_matched == len(expected_issues)
    return GradeResult(
        passed=passed,
        reasons=unmatched_reasons,
        merge_veto=False,
        extra={
            "extra_items": extra_items,
            "matched": total_matched,
            "expected": len(expected_issues),
        },
    )
