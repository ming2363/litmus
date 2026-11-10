"""测评报告数据聚合、有效性判定、Markdown 渲染与文件写出。"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from litmus.integrity import check_audit_during_run, check_run_integrity
from litmus.paths import get_repo_root, reports_dir
from litmus.report_html import render_html
from litmus.scoring import DIFFICULTY_WEIGHTS, compute_scores
from litmus.state import atomic_write_text, now_iso, parse_iso
from litmus.stats import wilson_interval
from litmus.tasks import VALID_DIFFICULTIES, TaskSpec, compute_bank_version, load_all_tasks
from litmus.usage import UsageSummary, collect


def sanitize_filename_part(value: str) -> str:
    """将不能用作文件名的字符（如 /、:、空格）替换为 '-'。"""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    cleaned = cleaned.strip("-")
    return cleaned or "unknown"


def build_report_filename_stem(
    state: Dict[str, Any], usage_summary: UsageSummary
) -> str:
    created_at = str(state.get("created_at") or now_iso())
    stamp = parse_iso(created_at).strftime("%Y%m%d-%H%M%S")
    tool = sanitize_filename_part(usage_summary.tool or "unknown")
    model_keys = sorted(usage_summary.models.keys())
    if len(model_keys) == 0:
        model = "unknown"
    elif len(model_keys) == 1:
        model = sanitize_filename_part(model_keys[0])
    else:
        model = sanitize_filename_part("+".join(model_keys))
    return "{}-{}-{}".format(stamp, tool, model)


def _group_stats(
    records: List[Dict[str, Any]],
    key: str,
    key_order: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    groups: Dict[str, List[bool]] = defaultdict(list)
    order_keys: List[str] = []
    for rec in records:
        k = str(rec[key])
        if k not in groups:
            order_keys.append(k)
        groups[k].append(bool(rec["passed"]))

    if key_order is not None:
        key_list = list(key_order)
        order_keys.sort(key=lambda k: key_list.index(k) if k in key_list else 999)

    rows: List[Dict[str, Any]] = []
    for k in order_keys:
        vals = groups[k]
        total = len(vals)
        passed = sum(1 for v in vals if v)
        rate = (float(passed) / total) if total else 0.0
        ci_low, ci_high = wilson_interval(passed, total)
        rows.append({
            "key": k,
            "passed": passed,
            "total": total,
            "rate": round(rate, 6),
            "ci_95": [round(ci_low, 6), round(ci_high, 6)],
        })
    return rows


def build_report_data(
    run_dir: Path,
    state: Dict[str, Any],
    tasks: Dict[str, TaskSpec],
    root: Optional[Path] = None,
    usage_summary: Optional[UsageSummary] = None,
    usage_kwargs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """构建完整机器可读报告字典。"""
    repo = get_repo_root(root)
    order: List[str] = list(state.get("order", []))
    results: Dict[str, Dict[str, Any]] = dict(state.get("results", {}))

    if usage_summary is None:
        uk = dict(usage_kwargs or {})
        usage_summary = collect(state.get("marker", ""), order, root=repo, **uk)

    # 汇总有效性判定原因（去重保序）
    raw_invalid: List[str] = []
    raw_invalid.extend(state.get("integrity_violations", []))
    raw_invalid.extend(check_run_integrity(state.get("head", ""), root=repo))
    raw_invalid.extend(
        check_audit_during_run(state.get("created_at", now_iso()), state.get("run_dir", ""), root=repo)
    )
    invalid_reasons: List[str] = []
    for r in raw_invalid:
        if r not in invalid_reasons:
            invalid_reasons.append(r)

    task_rows: List[Dict[str, Any]] = []
    merge_veto_count = 0
    incomplete_count = 0
    skipped_count = 0
    review_extra_items = 0
    total_elapsed_s = 0.0

    for idx, tid in enumerate(order, start=1):
        task = tasks[tid]
        rec = results.get(tid)
        token_bucket = usage_summary.by_task.get(tid)
        tokens_dict = token_bucket.to_dict() if token_bucket is not None else None

        if rec is None:
            status = "incomplete"
            passed = False
            merge_veto = False
            elapsed_s: Optional[float] = None
            seq = idx
            submitted_at = None
            reasons = ["未提交"]
            extra: Dict[str, Any] = {}
            incomplete_count += 1
        else:
            status = str(rec.get("status", "fail"))
            passed = status == "pass"
            merge_veto = bool(rec.get("merge_veto", False))
            elapsed_s = float(rec.get("elapsed_s", 0.0))
            seq = int(rec.get("seq", idx))
            submitted_at = rec.get("submitted_at")
            reasons = list(rec.get("reasons", []))
            extra = dict(rec.get("extra", {}))
            total_elapsed_s += elapsed_s
            if merge_veto:
                merge_veto_count += 1
            if status == "skipped":
                skipped_count += 1
            if task.grader == "review" and isinstance(extra.get("extra_items"), int):
                review_extra_items += int(extra["extra_items"])

        over_ref = elapsed_s is not None and elapsed_s > (task.ref_minutes * 60.0)
        task_rows.append({
            "id": tid,
            "seq": seq,
            "dimension": task.dimension,
            "difficulty": task.difficulty,
            "lang": task.lang,
            "grader": task.grader,
            "title": task.title,
            "status": status,
            "passed": passed,
            "merge_veto": merge_veto,
            "elapsed_s": round(elapsed_s, 3) if elapsed_s is not None else None,
            "ref_minutes": task.ref_minutes,
            "over_ref": over_ref,
            "submitted_at": submitted_at,
            "reasons": reasons,
            "extra": extra,
            "tokens": tokens_dict,
        })

    total = len(task_rows)
    passed_count = sum(1 for row in task_rows if row["passed"])
    score = (float(passed_count) / total) if total else 0.0
    score_ci = wilson_interval(passed_count, total)

    starts = list(state.get("starts", []))
    resumes = starts[1:] if len(starts) > 1 else []
    finished_at = state.get("finished_at") or now_iso()
    wall_s = max(
        0.0,
        (parse_iso(finished_at) - parse_iso(state.get("created_at", finished_at))).total_seconds(),
    )

    filename_stem = build_report_filename_stem(state, usage_summary)

    # 计算题库版本摘要与综合分
    bank_version = compute_bank_version(root=repo)
    score_result = compute_scores(task_rows, token_collected=usage_summary.collected)
    by_task_scores = score_result.get("by_task", {})

    # 将逐题明细回填到 task_rows，供逐题表渲染与机器可读导出
    for row in task_rows:
        detail = by_task_scores.get(row["id"])
        if detail:
            row["weight"] = detail["weight"]
            row["credit"] = detail["credit"]
            row["r"] = detail["r"]
            row["time_score"] = detail["time_score"]
            row["effective_tokens"] = detail["effective_tokens"]
            row["token_score"] = detail["token_score"]
        else:
            row["weight"] = DIFFICULTY_WEIGHTS.get(row.get("difficulty", "easy"), 1)
            row["credit"] = 1.0 if row["passed"] else 0.0
            row["r"] = None
            row["time_score"] = None
            row["effective_tokens"] = None
            row["token_score"] = None

    return {
        "report_id": filename_stem,
        "run_dir": state.get("run_dir"),
        "marker": state.get("marker"),
        "mode": state.get("mode"),
        "bank_version": bank_version,
        "started_at": state.get("created_at"),
        "finished_at": finished_at,
        "litmus_commit": state.get("head"),
        "env": dict(state.get("env", {})),
        "score": score_result,
        "validity": {
            "valid": len(invalid_reasons) == 0,
            "reasons": invalid_reasons,
        },
        "summary": {
            "passed": passed_count,
            "total": total,
            "score": round(score, 6),
            "ci_95": [round(score_ci[0], 6), round(score_ci[1], 6)],
            "merge_veto_count": merge_veto_count,
            "incomplete_count": incomplete_count,
            "skipped_count": skipped_count,
            "review_extra_items_total": review_extra_items,
            "total_elapsed_s": round(total_elapsed_s, 3),
            "wall_time_s": round(wall_s, 3),
        },
        "by_dimension": _group_stats(task_rows, "dimension"),
        "by_difficulty": _group_stats(task_rows, "difficulty", key_order=VALID_DIFFICULTIES),
        "interruptions": {
            "resume_count": len(resumes),
            "resumes": resumes,
        },
        "usage": {
            "collected": usage_summary.collected,
            "tool": usage_summary.tool,
            "note": usage_summary.note if not usage_summary.collected else "",
            "total": usage_summary.total.to_dict(),
            "models": {k: v.to_dict() for k, v in sorted(usage_summary.models.items())},
        },
        "tasks": task_rows,
    }


def _fmt_pct(val: float) -> str:
    return "{:.1f}%".format(val * 100.0)


def _format_score_parts(data: Dict[str, Any]) -> Dict[str, str]:
    """综合分各字段的展示文本。Markdown 与终端摘要共用，避免两处格式不一致。"""
    validity = data.get("validity") or {}
    score = data.get("score") or {}
    is_valid = bool(validity.get("valid", True))
    invalid_reasons = list(validity.get("reasons") or [])
    composite = score.get("composite")
    correctness = score.get("correctness")
    time_score = score.get("time_score")
    token_score = score.get("token_score")
    efficiency = score.get("efficiency")
    token_collected = bool(score.get("token_collected", True))

    if not is_valid:
        invalid_suffix = "（无效：{}）".format("；".join(invalid_reasons)) if invalid_reasons else "（无效）"
    else:
        invalid_suffix = ""
    if not token_collected:
        token_str = "未采集（效率系数只用时间分）"
    elif token_score is not None:
        token_str = "{:.2f}".format(token_score)
    else:
        token_str = "无"

    return {
        "composite": "{:.2f}".format(composite) if composite is not None else "0.00",
        "invalid_suffix": invalid_suffix,
        "correctness": "{:.2f}".format(correctness) if correctness is not None else "0.00",
        "time": "{:.2f}".format(time_score) if time_score is not None else "无",
        "token": token_str,
        "efficiency": "{:.2f}".format(efficiency) if efficiency is not None else "无",
    }


def render_terminal_summary(data: Dict[str, Any]) -> str:
    """终端简短摘要：综合分、四个分项和计数，不含表格。"""
    parts = _format_score_parts(data)
    summary = data.get("summary") or {}
    lines = [
        "综合分：{}{}".format(parts["composite"], parts["invalid_suffix"]),
        "正确性分：{} | 时间分：{} | token 分：{} | 效率系数：{}".format(
            parts["correctness"], parts["time"], parts["token"], parts["efficiency"]
        ),
        "通过 {}/{} 题，可合入性否决 {}，未完成 {}，跳过 {}".format(
            summary.get("passed", 0),
            summary.get("total", 0),
            summary.get("merge_veto_count", 0),
            summary.get("incomplete_count", 0),
            summary.get("skipped_count", 0),
        ),
    ]
    return "\n".join(lines) + "\n"


def render_markdown(data: Dict[str, Any]) -> str:
    """将报告字典渲染为客观指标 Markdown 文本。"""
    s = data["summary"]
    v = data["validity"]
    u = data["usage"]
    intr = data["interruptions"]
    env = data.get("env", {})
    is_valid = bool(v.get("valid", True))
    invalid_reasons = list(v.get("reasons", []))

    parts = _format_score_parts(data)

    lines: List[str] = [
        "# litmus 测评报告 ({})".format(data["report_id"]),
        "",
        "## 综合分：{}{}".format(parts["composite"], parts["invalid_suffix"]),
        "- 正确性分：{} | 时间分：{} | token 分：{} | 效率系数：{}".format(
            parts["correctness"], parts["time"], parts["token"], parts["efficiency"]
        ),
        "",
        "## 基本信息与有效性",
        "- 成绩有效性：**{}**{}".format(
            "有效" if is_valid else "无效",
            "" if is_valid else "（原因：{}）".format("；".join(invalid_reasons)),
        ),
        "- 测评模式：{} | 运行目录：{} | 运行标记：{}".format(
            data["mode"], data["run_dir"], data["marker"]
        ),
        "- 题库版本：`{}`".format(data.get("bank_version") or "unknown"),
        "- 工具名称：{} | 模型列表：{}".format(
            u["tool"] if u["collected"] else "未采集",
            ", ".join(u["models"].keys()) if u["models"] else ("未采集" if not u["collected"] else "unknown"),
        ),
        "- litmus 提交号：`{}`".format(data.get("litmus_commit") or "unknown"),
        "- 环境版本：Python {} / {} / {}".format(
            env.get("python_version", "unknown"),
            env.get("java_version", "unknown"),
            env.get("javac_version", "unknown"),
        ),
        "- 起止时间：{} ～ {}（总墙钟耗时 {:.1f}s，做题累计耗时 {:.1f}s）".format(
            data["started_at"], data["finished_at"], s["wall_time_s"], s["total_elapsed_s"]
        ),
        "",
        "## 总分与计数指标",
        "| 指标 | 数值 |",
        "|---|---|",
        "| 总分（等权） | {}/{} ({}，95% Wilson CI: [{}%, {}%]) |".format(
            s["passed"],
            s["total"],
            _fmt_pct(s["score"]),
            round(s["ci_95"][0] * 100.0, 1),
            round(s["ci_95"][1] * 100.0, 1),
        ),
        "| 可合入性否决数 | {} |".format(s["merge_veto_count"]),
        "| 未完成数（计为不通过） | {} |".format(s["incomplete_count"]),
        "| 跳过数 | {} |".format(s["skipped_count"]),
        "| Code Review 额外条目数 | {} |".format(s["review_extra_items_total"]),
        "| 中断续跑次数 | {} |".format(intr["resume_count"]),
        "",
        "## 按维度通过率",
        "| 维度 | 通过/总数 | 通过率 | 95% Wilson 置信区间 |",
        "|---|---|---|---|",
    ]
    for row in data["by_dimension"]:
        lines.append(
            "| {} | {}/{} | {} | [{}%, {}%] |".format(
                row["key"],
                row["passed"],
                row["total"],
                _fmt_pct(row["rate"]),
                round(row["ci_95"][0] * 100.0, 1),
                round(row["ci_95"][1] * 100.0, 1),
            )
        )

    lines.extend([
        "",
        "## 按难度通过率",
        "| 难度 | 通过/总数 | 通过率 | 95% Wilson 置信区间 |",
        "|---|---|---|---|",
    ])
    for row in data["by_difficulty"]:
        lines.append(
            "| {} | {}/{} | {} | [{}%, {}%] |".format(
                row["key"],
                row["passed"],
                row["total"],
                _fmt_pct(row["rate"]),
                round(row["ci_95"][0] * 100.0, 1),
                round(row["ci_95"][1] * 100.0, 1),
            )
        )

    lines.extend([
        "",
        "## Token 用量",
    ])
    if not u["collected"]:
        lines.append("- 状态：未采集")
    else:
        tot = u["total"]
        lines.append(
            "- 合计：输入 {} / 输出 {} / 缓存读取 {} / 缓存写入 {} / 思考 {}".format(
                tot["input_tokens"],
                tot["output_tokens"],
                tot["cache_read_tokens"],
                tot["cache_write_tokens"],
                tot["reasoning_tokens"],
            )
        )
        lines.append("")
        lines.append("| 模型 ID | 输入 | 输出 | 缓存读取 | 缓存写入 | 思考 |")
        lines.append("|---|---|---|---|---|---|")
        for mid, tb in u["models"].items():
            lines.append(
                "| {} | {} | {} | {} | {} | {} |".format(
                    mid,
                    tb["input_tokens"],
                    tb["output_tokens"],
                    tb["cache_read_tokens"],
                    tb["cache_write_tokens"],
                    tb["reasoning_tokens"],
                )
            )

    if intr["resume_count"] > 0:
        lines.extend(["", "## 中断续跑记录"])
        for item in intr["resumes"]:
            lines.append("- {} 在题目 {} 重新执行 start".format(item.get("at"), item.get("at_task") or "未发题"))

    lines.extend([
        "",
        "## 逐题明细",
        "| 序号 | 题号 | 维度 | 难度 | 状态 | 得分比例 | 可合入性否决 | 耗时(s) | 参考(min) | r | 时间得分 | 计费等价 token | token 得分 | 备注 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ])
    for t in data["tasks"]:
        elapsed_str = "-" if t["elapsed_s"] is None else "{:.1f}".format(t["elapsed_s"])
        r_str = "-" if t.get("r") is None else "{:.2f}".format(t["r"])
        time_score_str = "-" if t.get("time_score") is None else "{:.2f}".format(t["time_score"])
        eff_tokens_str = "-" if t.get("effective_tokens") is None else str(int(round(t["effective_tokens"])))
        token_score_str = "-" if t.get("token_score") is None else "{:.2f}".format(t["token_score"])
        credit = t.get("credit")
        if credit is None:  # 旧版报告数据没有得分比例，按通过与否补
            credit = 1.0 if t.get("passed") else 0.0
        credit_str = "{:.0%}".format(credit)
        notes: List[str] = []
        if t["status"] == "incomplete":
            notes.append("未完成")
        if t["over_ref"]:
            notes.append("超过参考时长")
        if t["reasons"] and not t["passed"] and t["status"] != "incomplete":
            notes.append("; ".join(t["reasons"])[:120])
        lines.append(
            "| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                t["seq"],
                t["id"],
                t["dimension"],
                t["difficulty"],
                t["status"],
                credit_str,
                "是" if t["merge_veto"] else "否",
                elapsed_str,
                t["ref_minutes"],
                r_str,
                time_score_str,
                eff_tokens_str,
                token_score_str,
                "；".join(notes) if notes else "-",
            )
        )

    return "\n".join(lines) + "\n"


def write_report_files(
    report_data: Dict[str, Any], root: Optional[Path] = None
) -> Tuple[Path, Path, Path]:
    """写出 HTML、Markdown 和 JSON。返回 (html_path, md_path, json_path)。"""
    rdir = reports_dir(root)
    rdir.mkdir(parents=True, exist_ok=True)
    stem = report_data["report_id"]
    html_path = rdir / "{}.html".format(stem)
    md_path = rdir / "{}.md".format(stem)
    json_path = rdir / "{}.json".format(stem)

    atomic_write_text(html_path, render_html(report_data))
    atomic_write_text(md_path, render_markdown(report_data))
    atomic_write_text(json_path, json.dumps(report_data, ensure_ascii=False, indent=2) + "\n")
    return html_path, md_path, json_path


def generate_and_write_report(
    run_dir: Path,
    state: Dict[str, Any],
    root: Optional[Path] = None,
    usage_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], str, Path, Path, Path]:
    """生成报告并写文件。返回 (数据, Markdown 文本, html 路径, md 路径, json 路径)。"""
    _, tasks = load_all_tasks(root)
    report_data = build_report_data(
        run_dir, state, tasks, root=root, usage_kwargs=usage_kwargs
    )
    md_text = render_markdown(report_data)
    html_path, md_path, json_path = write_report_files(report_data, root=root)
    return report_data, md_text, html_path, md_path, json_path
