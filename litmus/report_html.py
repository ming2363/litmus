"""把测评报告渲染成单文件、可离线打开的 HTML。

样式和脚本全部内联，不引用外部资源。所有来自报告数据的字符串都经
html.escape 转义后再进入页面，避免失败原因里的报错文本形成注入。
"""

import html
from typing import Any, Callable, Dict, List, Optional, Sequence

# 维度、难度只翻译已知键；不认识的键原样显示，避免把新题型显示成空白。
_DIMENSION_LABELS = {
    "bug": "修 Bug",
    "feature": "新功能",
    "terminal": "终端实操",
    "tool_call": "工具调用",
    "read_code": "读代码",
    "edit": "小范围编辑",
    "review": "Code Review",
}
_DIFFICULTY_LABELS = {
    "easy": "易",
    "medium": "中",
    "hard": "难",
    "long": "长任务",
}
# 难度排序用固定序号，不按中文拼音排。
_DIFFICULTY_ORDER = {"easy": "0", "medium": "1", "hard": "2", "long": "3"}

_STATUS_LABELS = {
    "pass": "通过",
    "fail": "不通过",
    "partial": "部分得分",
    "incomplete": "未完成",
    "skipped": "跳过",
    "veto": "否决",
}

# 逐题表列与 Markdown 版一致。kind 只影响数字列右对齐。
_TASK_COLUMNS = (
    ("seq", "序号", "num"),
    ("id", "题号", "text"),
    ("dimension", "维度", "text"),
    ("difficulty", "难度", "num"),
    ("status", "状态", "text"),
    ("credit", "得分比例", "num"),
    ("veto", "可合入性否决", "num"),
    ("elapsed", "耗时(s)", "num"),
    ("ref", "参考时长(min)", "num"),
    ("r", "r", "num"),
    ("time_score", "时间得分", "num"),
    ("tokens", "计费等价 token", "num"),
    ("token_score", "token 得分", "num"),
    ("notes", "备注", "text"),
)


def _e(value: Any) -> str:
    """转义后才能放进文本或属性。None 变成空串。"""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _text(value: Any, fallback: str = "unknown") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def _fmt_fixed(value: Any, digits: int = 2, missing: str = "无") -> str:
    if value is None:
        return missing
    try:
        return "{:.{}f}".format(float(value), digits)
    except (TypeError, ValueError):
        return missing


def _fmt_pct(value: Any) -> str:
    try:
        return "{:.1f}%".format(float(value) * 100.0)
    except (TypeError, ValueError):
        return "-"


def _ci_text(ci: Any) -> str:
    if not isinstance(ci, (list, tuple)) or len(ci) < 2:
        return "-"
    try:
        low = round(float(ci[0]) * 100.0, 1)
        high = round(float(ci[1]) * 100.0, 1)
    except (TypeError, ValueError):
        return "-"
    return "[{}%, {}%]".format(low, high)


def _bar_width(rate: Any) -> str:
    """条形宽度只接受格式化后的数字，不把原始字段拼进 style。"""
    try:
        val = float(rate)
    except (TypeError, ValueError):
        val = 0.0
    if val != val:  # NaN
        val = 0.0
    if val < 0.0:
        val = 0.0
    if val > 1.0:
        val = 1.0
    return "{:.1f}".format(val * 100.0)


def _dimension_label(key: str) -> str:
    return _DIMENSION_LABELS.get(key, key)


def _difficulty_label(key: str) -> str:
    return _DIFFICULTY_LABELS.get(key, key)


def _credit_value(task: Dict[str, Any]) -> float:
    credit = task.get("credit")
    if credit is None:
        return 1.0 if task.get("passed") else 0.0
    try:
        return float(credit)
    except (TypeError, ValueError):
        return 0.0


def _status_key(task: Dict[str, Any]) -> str:
    """状态标签优先级：跳过、未完成、否决、部分得分、通过、不通过。"""
    status = str(task.get("status") or "")
    if status == "skipped":
        return "skipped"
    if status == "incomplete":
        return "incomplete"
    if bool(task.get("merge_veto")):
        return "veto"
    credit = _credit_value(task)
    if 0.0 < credit < 1.0:
        return "partial"
    if bool(task.get("passed")) or status == "pass":
        return "pass"
    return "fail"


def _opt_num(value: Any, display_spec: str) -> Optional[str]:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return display_spec.format(number)


def _token_int(bucket: Dict[str, Any], key: str) -> str:
    try:
        return str(int(bucket.get(key, 0) or 0))
    except (TypeError, ValueError):
        return str(bucket.get(key, 0))


def _render_hero(data: Dict[str, Any]) -> str:
    validity = data.get("validity") or {}
    usage = data.get("usage") or {}
    score = data.get("score") or {}
    is_valid = bool(validity.get("valid", True))
    reasons = [str(item) for item in _as_list(validity.get("reasons")) if str(item) != ""]
    composite = score.get("composite")
    composite_text = "{:.2f}".format(float(composite)) if composite is not None else "0.00"

    if is_valid:
        badge = '<span class="badge tag-pass">有效</span>'
    else:
        badge = '<span class="badge tag-fail">无效</span>'
        if reasons:
            badge += '<span class="invalid-reasons">{}</span>'.format(_e("；".join(reasons)))

    if usage.get("collected"):
        tool = _text(usage.get("tool"))
        model_map = usage.get("models") or {}
        if isinstance(model_map, dict) and model_map:
            models = ", ".join(str(key) for key in model_map.keys())
        else:
            models = "unknown"
    else:
        tool = "未采集"
        models = "未采集"

    meta_items = (
        ("模式", _text(data.get("mode"))),
        ("题库版本", _text(data.get("bank_version"))),
        ("工具", tool),
        ("模型", models),
        ("开始", _text(data.get("started_at"), "-")),
        ("结束", _text(data.get("finished_at"), "-")),
    )
    meta_html = "".join(
        "<span>{}：{}</span>".format(_e(label), _e(value)) for label, value in meta_items
    )
    report_id = _text(data.get("report_id"), "")
    return "\n".join([
        '<header class="hero-block">',
        "<h1>litmus 测评报告</h1>",
        '<p class="report-id">{}</p>'.format(_e(report_id)),
        '<div class="hero">',
        "<div>",
        '<p class="composite-label">综合分</p>',
        '<p class="composite">{}</p>'.format(_e(composite_text)),
        "</div>",
        '<div class="validity">{}</div>'.format(badge),
        "</div>",
        '<p class="meta">{}</p>'.format(meta_html),
        "</header>",
    ])


def _render_cards(data: Dict[str, Any]) -> str:
    score = data.get("score") or {}
    token_collected = bool(score.get("token_collected", True))
    cards = [
        ("正确性分", _fmt_fixed(score.get("correctness")), ""),
        ("时间分", _fmt_fixed(score.get("time_score")), ""),
        (
            "token 分",
            "未采集" if not token_collected else _fmt_fixed(score.get("token_score")),
            "效率系数只用时间分" if not token_collected else "",
        ),
        ("效率系数", _fmt_fixed(score.get("efficiency")), ""),
    ]
    parts = ['<section>', '<h2 class="sr-only">分项得分</h2>', '<div class="cards">']
    for title, value, note in cards:
        note_html = '<p class="card-note">{}</p>'.format(_e(note)) if note else ""
        parts.append(
            '<article class="card"><h3>{}</h3><p class="card-value">{}</p>{}</article>'.format(
                _e(title), _e(value), note_html
            )
        )
    parts.append("</div>")
    parts.append('<p class="formula">综合分 = 正确性分 × 效率系数</p>')
    parts.append("</section>")
    return "\n".join(parts)


def _render_counts(data: Dict[str, Any]) -> str:
    summary = data.get("summary") or {}
    intr = data.get("interruptions") or {}
    passed = summary.get("passed", 0)
    total = summary.get("total", 0)
    items = (
        ("通过题数 / 总题数", "{}/{}".format(passed, total), "95% Wilson 区间 {}".format(_ci_text(summary.get("ci_95")))),
        ("可合入性否决数", str(summary.get("merge_veto_count", 0)), ""),
        ("未完成数", str(summary.get("incomplete_count", 0)), ""),
        ("跳过数", str(summary.get("skipped_count", 0)), ""),
        ("Code Review 额外条目数", str(summary.get("review_extra_items_total", 0)), ""),
        ("中断续跑次数", str(intr.get("resume_count", 0)), ""),
    )
    parts = ["<section>", "<h2>总览</h2>", '<div class="count-grid">']
    for label, value, extra in items:
        extra_html = '<span class="s">{}</span>'.format(_e(extra)) if extra else ""
        parts.append(
            '<div class="count"><span class="k">{}</span><span class="v">{}</span>{}</div>'.format(
                _e(label), _e(value), extra_html
            )
        )
    parts.append("</div></section>")
    return "\n".join(parts)


def _render_bars(title: str, rows: Sequence[Any], labeler: Callable[[str], str]) -> str:
    parts = ["<section>", "<h2>{}</h2>".format(_e(title))]
    usable = [row for row in rows if isinstance(row, dict)]
    if not usable:
        parts.append('<p class="muted">无</p>')
        parts.append("</section>")
        return "\n".join(parts)
    parts.append('<div class="bars">')
    for row in usable:
        key = str(row.get("key", ""))
        rate = row.get("rate", 0)
        meta = "{} / {} · {} · {}".format(
            row.get("passed", 0),
            row.get("total", 0),
            _fmt_pct(rate),
            _ci_text(row.get("ci_95")),
        )
        parts.append(
            '<div class="bar-row">'
            '<div class="bar-label">{}</div>'
            '<div class="bar-track" aria-hidden="true"><div class="bar-fill" style="width: {}%"></div></div>'
            '<div class="bar-meta">{}</div>'
            "</div>".format(_e(labeler(key)), _bar_width(rate), _e(meta))
        )
    parts.append("</div></section>")
    return "\n".join(parts)


def _render_usage(data: Dict[str, Any]) -> str:
    usage = data.get("usage") or {}
    parts = ["<section>", "<h2>Token 用量</h2>"]
    if not usage.get("collected"):
        parts.append('<p class="card-value">未采集</p>')
        note = str(usage.get("note") or "").strip()
        if note and note != "未采集":
            parts.append("<p>原因：{}</p>".format(_e(note)))
        parts.append("</section>")
        return "\n".join(parts)

    total = usage.get("total") if isinstance(usage.get("total"), dict) else {}
    parts.append(
        "<p>合计：输入 {} / 输出 {} / 缓存读取 {} / 缓存写入 {} / 思考 {}</p>".format(
            _e(_token_int(total, "input_tokens")),
            _e(_token_int(total, "output_tokens")),
            _e(_token_int(total, "cache_read_tokens")),
            _e(_token_int(total, "cache_write_tokens")),
            _e(_token_int(total, "reasoning_tokens")),
        )
    )
    parts.append('<div class="table-scroll"><table>')
    parts.append(
        "<thead><tr>"
        "<th>模型 ID</th><th class=\"num\">输入</th><th class=\"num\">输出</th>"
        "<th class=\"num\">缓存读取</th><th class=\"num\">缓存写入</th><th class=\"num\">思考</th>"
        "</tr></thead><tbody>"
    )
    models = usage.get("models") if isinstance(usage.get("models"), dict) else {}
    if not models:
        parts.append('<tr><td colspan="6">无</td></tr>')
    else:
        for model_id, bucket in models.items():
            item = bucket if isinstance(bucket, dict) else {}
            parts.append(
                "<tr><td>{}</td><td class=\"num\">{}</td><td class=\"num\">{}</td>"
                "<td class=\"num\">{}</td><td class=\"num\">{}</td><td class=\"num\">{}</td></tr>".format(
                    _e(model_id),
                    _e(_token_int(item, "input_tokens")),
                    _e(_token_int(item, "output_tokens")),
                    _e(_token_int(item, "cache_read_tokens")),
                    _e(_token_int(item, "cache_write_tokens")),
                    _e(_token_int(item, "reasoning_tokens")),
                )
            )
    parts.append("</tbody></table></div></section>")
    return "\n".join(parts)


def _notes_cell(task: Dict[str, Any]) -> str:
    notes: List[str] = []
    if str(task.get("status") or "") == "incomplete":
        notes.append("未完成")
    if task.get("over_ref"):
        notes.append("超过参考时长")
    if not notes:
        return "-"
    return '<span class="note-text">{}</span>'.format(_e("；".join(notes)))


def _failure_reasons(task: Dict[str, Any]) -> List[str]:
    """没得满分的题才展示失败原因；通过的题不做空折叠块。"""
    if task.get("passed"):
        return []
    return [str(item) for item in _as_list(task.get("reasons")) if str(item) != ""]


def _task_cells(task: Dict[str, Any], seq_fallback: int) -> List[str]:
    status_key = _status_key(task)
    status_html = '<span class="tag tag-{}">{}</span>'.format(
        status_key, _e(_STATUS_LABELS[status_key])
    )
    credit = _credit_value(task)
    credit_text = "{:.0%}".format(credit)
    dimension = str(task.get("dimension") or "")
    difficulty = str(task.get("difficulty") or "")
    elapsed = _opt_num(task.get("elapsed_s"), "{:.1f}")
    ref = task.get("ref_minutes")
    ref_text = None if ref is None or ref == "" else str(ref)
    ratio = _opt_num(task.get("r"), "{:.2f}")
    time_score = _opt_num(task.get("time_score"), "{:.2f}")
    token_score = _opt_num(task.get("token_score"), "{:.2f}")
    tokens_raw = task.get("effective_tokens")
    if tokens_raw is None or tokens_raw == "":
        tokens_text = None
    else:
        try:
            tokens_text = str(int(round(float(tokens_raw))))
        except (TypeError, ValueError):
            tokens_text = None

    seq = task.get("seq", seq_fallback)
    cells = {
        "seq": (str(seq), str(seq), False),
        "id": (str(task.get("id") or ""), str(task.get("id") or ""), False),
        "dimension": (_dimension_label(dimension), _dimension_label(dimension), False),
        "difficulty": (
            _difficulty_label(difficulty),
            _DIFFICULTY_ORDER.get(difficulty, difficulty),
            True,
        ),
        "status": (status_html, _STATUS_LABELS[status_key], False),
        "credit": (credit_text, "{:.6f}".format(credit), True),
        "veto": ("是" if task.get("merge_veto") else "否", "1" if task.get("merge_veto") else "0", True),
        "elapsed": (elapsed or "-", "" if elapsed is None else str(task.get("elapsed_s")), True),
        "ref": (ref_text or "-", "" if ref_text is None else str(ref), True),
        "r": (ratio or "-", "" if ratio is None else str(task.get("r")), True),
        "time_score": (time_score or "-", "" if time_score is None else str(task.get("time_score")), True),
        "tokens": (tokens_text or "-", "" if tokens_text is None else tokens_text, True),
        "token_score": (token_score or "-", "" if token_score is None else str(task.get("token_score")), True),
        "notes": (_notes_cell(task), "；".join(
            [item for item in ("未完成" if str(task.get("status") or "") == "incomplete" else "", "超过参考时长" if task.get("over_ref") else "") if item]
        ), False),
    }
    rendered: List[str] = []
    for key, _label, kind in _TASK_COLUMNS:
        display, sort_value, numeric = cells[key]
        css = "num" if numeric or kind == "num" else ""
        if key == "notes":
            css = "notes"
        class_attr = ' class="{}"'.format(css) if css else ""
        # status 和 notes 的 display 已是转义后的 HTML，其余列是纯文本，这里统一转义纯文本。
        if key in ("status", "notes"):
            inner = display
        else:
            inner = _e(display)
        rendered.append(
            "<td{} data-value=\"{}\">{}</td>".format(class_attr, _e(sort_value), inner)
        )
    return rendered


def _render_tasks(data: Dict[str, Any]) -> str:
    tasks = [task for task in _as_list(data.get("tasks")) if isinstance(task, dict)]
    seen = []
    for task in tasks:
        key = str(task.get("dimension") or "")
        if key not in seen:
            seen.append(key)
    status_options = ['<option value="">全部</option>']
    for key in ("pass", "fail", "partial", "incomplete", "skipped", "veto"):
        status_options.append(
            '<option value="{}">{}</option>'.format(key, _e(_STATUS_LABELS[key]))
        )
    dim_options = ['<option value="">全部</option>']
    for key in seen:
        if key == "":
            continue
        dim_options.append(
            '<option value="{}">{}</option>'.format(_e(key), _e(_dimension_label(key)))
        )
    parts = [
        "<section>",
        "<h2>逐题明细</h2>",
        '<div class="filters">',
        '<label>状态<select id="filter-status">{}</select></label>'.format("".join(status_options)),
        '<label>维度<select id="filter-dimension">{}</select></label>'.format("".join(dim_options)),
        "</div>",
        '<div class="table-scroll">',
        '<table id="task-table">',
        "<thead><tr>",
    ]
    for _key, label, kind in _TASK_COLUMNS:
        class_attr = ' class="num"' if kind == "num" else ""
        parts.append("<th{} scope=\"col\">{}</th>".format(class_attr, _e(label)))
    parts.append("</tr></thead><tbody>")
    for index, task in enumerate(tasks, start=1):
        status_key = _status_key(task)
        dimension = str(task.get("dimension") or "")
        reasons = _failure_reasons(task)
        parts.append(
            '<tr class="task-row{}" data-status="{}" data-dimension="{}">{}</tr>'.format(
                " has-reason" if reasons else "",
                _e(status_key),
                _e(dimension),
                "".join(_task_cells(task, index)),
            )
        )
        # 失败原因单独占一整行、默认收起：放在窄列里长报错会被挤成很高的一条
        if reasons:
            parts.append(
                '<tr class="reason-row" data-status="{}" data-dimension="{}">'
                '<td colspan="{}"><details><summary>{} 失败原因</summary><pre>{}</pre></details></td></tr>'.format(
                    _e(status_key),
                    _e(dimension),
                    len(_TASK_COLUMNS),
                    _e(task.get("id") or ""),
                    _e("\n".join(reasons)),
                )
            )
    parts.append("</tbody></table></div></section>")
    return "\n".join(parts)


def _render_interruptions(data: Dict[str, Any]) -> str:
    intr = data.get("interruptions") or {}
    resumes = [item for item in _as_list(intr.get("resumes")) if isinstance(item, dict)]
    try:
        count = int(intr.get("resume_count") or 0)
    except (TypeError, ValueError):
        count = 0
    if count <= 0 and not resumes:
        return ""
    parts = ["<section>", "<h2>中断续跑记录</h2>", "<ul>"]
    for item in resumes:
        at_task = item.get("at_task") or "未发题"
        parts.append(
            "<li>{} 在题目 {} 重新执行 start</li>".format(_e(item.get("at")), _e(at_task))
        )
    if not resumes:
        parts.append("<li>中断续跑 {} 次</li>".format(_e(count)))
    parts.append("</ul></section>")
    return "\n".join(parts)


def _render_env(data: Dict[str, Any]) -> str:
    env = data.get("env") if isinstance(data.get("env"), dict) else {}
    rows = (
        ("Python", _text(env.get("python_version"))),
        ("Java", _text(env.get("java_version"))),
        ("javac", _text(env.get("javac_version"))),
        ("litmus 提交号", _text(data.get("litmus_commit"))),
        ("运行目录", _text(data.get("run_dir"), "-")),
        ("运行标记", _text(data.get("marker"), "-")),
    )
    items = [
        "<li><span>{}</span><span>{}</span></li>".format(_e(label), _e(value))
        for label, value in rows
    ]
    return "\n".join([
        "<section>",
        "<h2>运行环境</h2>",
        '<ul class="env">',
        "".join(items),
        "</ul>",
        "</section>",
    ])


_CSS = """
:root {
  color-scheme: light;
  --bg: #f5f6f8;
  --card: #ffffff;
  --text: #1f2328;
  --muted: #656d76;
  --line: #d8dee4;
  --accent: #0969da;
  --accent-text: #0969da;
  --track: #eaeef2;
  --hover: #f6f8fa;
  --pre-bg: #f6f8fa;
  --pass-fg: #1a7f37;
  --pass-bg: #dafbe1;
  --fail-fg: #cf222e;
  --fail-bg: #ffebe9;
  --partial-fg: #9a6700;
  --partial-bg: #fff8c5;
  --incomplete-fg: #57606a;
  --incomplete-bg: #eaeef2;
  --skipped-fg: #0969da;
  --skipped-bg: #ddf4ff;
  --veto-fg: #8250df;
  --veto-bg: #fbefff;
  --shadow: 0 1px 2px rgba(31, 35, 40, 0.06);
}
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --bg: #0d1117;
    --card: #161b22;
    --text: #e6edf3;
    --muted: #8d96a0;
    --line: #30363d;
    --accent: #4493f8;
    --accent-text: #79b8ff;
    --track: #21262d;
    --hover: #1c2128;
    --pre-bg: #0d1117;
    --pass-fg: #3fb950;
    --pass-bg: #033a16;
    --fail-fg: #f85149;
    --fail-bg: #490202;
    --partial-fg: #d4a72c;
    --partial-bg: #3b2d08;
    --incomplete-fg: #8d96a0;
    --incomplete-bg: #21262d;
    --skipped-fg: #79b8ff;
    --skipped-bg: #04294f;
    --veto-fg: #d2a8ff;
    --veto-bg: #2e1a47;
    --shadow: none;
  }
}
* { box-sizing: border-box; }
html { max-width: 100%; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  line-height: 1.5;
}
.wrap { width: 100%; max-width: 1280px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { margin: 0; font-size: 1rem; font-weight: 600; color: var(--muted); }
h2 { margin: 0 0 12px; font-size: 1.15rem; }
h3 { margin: 0; font-size: 0.85rem; font-weight: 600; color: var(--muted); }
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
.report-id { margin: 4px 0 0; color: var(--muted); font-size: 0.85rem; overflow-wrap: anywhere; }
.hero { display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between; gap: 12px 24px; margin-top: 12px; }
.composite-label { margin: 0; color: var(--muted); }
.composite {
  margin: 0;
  font-size: clamp(3rem, 12vw, 5rem);
  font-weight: 700;
  letter-spacing: -0.04em;
  line-height: 0.95;
  font-variant-numeric: tabular-nums;
}
.validity { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; max-width: 100%; }
.invalid-reasons { color: var(--fail-fg); overflow-wrap: anywhere; }
.meta { display: flex; flex-wrap: wrap; gap: 6px 16px; margin: 14px 0 0; color: var(--muted); }
.meta span { overflow-wrap: anywhere; }
.badge, .tag {
  display: inline-block;
  border-radius: 999px;
  font-weight: 650;
  line-height: 1.4;
  white-space: nowrap;
}
.badge { padding: 0.28em 0.8em; font-size: 1rem; }
.tag { padding: 0.12em 0.55em; font-size: 0.82rem; }
.tag-pass { color: var(--pass-fg); background: var(--pass-bg); }
.tag-fail { color: var(--fail-fg); background: var(--fail-bg); }
.tag-partial { color: var(--partial-fg); background: var(--partial-bg); }
.tag-incomplete { color: var(--incomplete-fg); background: var(--incomplete-bg); }
.tag-skipped { color: var(--skipped-fg); background: var(--skipped-bg); }
.tag-veto { color: var(--veto-fg); background: var(--veto-bg); }
section { margin-top: 28px; }
.cards, .count-grid { display: grid; gap: 12px; }
.cards { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.count-grid { grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
.card, .count {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 14px 16px;
  min-width: 0;
}
.card-value, .count .v {
  margin: 8px 0 0;
  font-size: 1.55rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  overflow-wrap: anywhere;
}
.card-note, .formula, .muted, .count .s, .count .k { color: var(--muted); }
.card-note { margin: 6px 0 0; font-size: 0.85rem; }
.formula { margin: 12px 0 0; }
.count .k, .count .s { display: block; font-size: 0.8rem; }
.count .v { font-size: 1.25rem; }
.bar-row {
  display: grid;
  grid-template-columns: minmax(5.5rem, 8.5rem) minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  margin: 8px 0;
}
.bar-label { overflow-wrap: anywhere; }
.bar-track { height: 10px; background: var(--track); border-radius: 999px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--accent); border-radius: 999px; }
.bar-meta { color: var(--muted); font-size: 0.85rem; font-variant-numeric: tabular-nums; white-space: nowrap; }
.filters { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 10px; }
.filters label { display: flex; flex-direction: column; gap: 4px; color: var(--muted); font-size: 0.8rem; }
select, button {
  font: inherit;
  color: var(--text);
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 6px 8px;
}
.table-scroll { width: 100%; max-width: 100%; overflow-x: auto; }
table { border-collapse: collapse; width: 100%; }
th, td {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid var(--line);
  font-size: 0.88rem;
  vertical-align: top;
}
th { cursor: pointer; user-select: none; background: var(--card); vertical-align: bottom; min-width: 3.2em; }
th:hover { color: var(--accent-text); }
th[data-sort-dir="asc"]::after { content: " ↑"; }
th[data-sort-dir="desc"]::after { content: " ↓"; }
td { white-space: nowrap; }
td.notes { white-space: normal; min-width: 6rem; max-width: 12rem; }
tr.has-reason td { border-bottom: none; }
tr.reason-row td { white-space: normal; padding-top: 0; }
tbody tr.reason-row:hover { background: transparent; }
.num { text-align: right; font-variant-numeric: tabular-nums; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
tbody tr:hover { background: var(--hover); }
details summary { cursor: pointer; color: var(--accent-text); }
details pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  margin: 8px 0 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.82rem;
  background: var(--pre-bg);
  padding: 8px 10px;
  border-radius: 8px;
}
.env { list-style: none; padding: 0; margin: 0; }
.env li {
  display: grid;
  grid-template-columns: minmax(7rem, 10rem) minmax(0, 1fr);
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid var(--line);
}
.env li span:first-child { color: var(--muted); }
.env li span:last-child { overflow-wrap: anywhere; font-variant-numeric: tabular-nums; }
@media (max-width: 800px) {
  .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .bar-row { grid-template-columns: 1fr; }
  .bar-meta { white-space: normal; }
}
@media (max-width: 480px) {
  .cards { grid-template-columns: 1fr; }
}
@media print {
  .filters { display: none !important; }
  body { background: #fff; color: #000; }
  .card, .count { box-shadow: none; }
}
"""

# 筛选和排序只改已经渲染好的行，不把报告数据再塞进脚本。
# 没有执行这段脚本时，表格行保持默认显示，内容仍然完整。
_JS = """
(function () {
  var table = document.getElementById("task-table");
  var statusSel = document.getElementById("filter-status");
  var dimSel = document.getElementById("filter-dimension");

  function applyFilter() {
    if (!table || !table.tBodies.length) return;
    var st = statusSel ? statusSel.value : "";
    var dim = dimSel ? dimSel.value : "";
    var rows = table.tBodies[0].rows;
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i];
      var ok = true;
      if (st && row.getAttribute("data-status") !== st) ok = false;
      if (dim && row.getAttribute("data-dimension") !== dim) ok = false;
      row.style.display = ok ? "" : "none";
    }
  }
  if (statusSel) statusSel.addEventListener("change", applyFilter);
  if (dimSel) dimSel.addEventListener("change", applyFilter);
  if (!table || !table.tHead || !table.tBodies.length) return;

  var headers = table.tHead.rows[0].cells;
  var sortState = { idx: -1, asc: true };

  function cellValue(row, idx) {
    var cell = row.cells[idx];
    if (!cell) return null;
    var raw = cell.getAttribute("data-value");
    if (raw === null || raw === "") return null;
    if (/^-?\\d+(\\.\\d+)?$/.test(raw)) return parseFloat(raw);
    return raw;
  }

  function sortBy(idx) {
    var asc = sortState.idx === idx ? !sortState.asc : true;
    sortState = { idx: idx, asc: asc };
    var body = table.tBodies[0];
    // 只给题目行排序；失败原因行跟在所属题目行后面一起移动
    var rows = Array.prototype.filter.call(body.rows, function (r) {
      return r.className.indexOf("reason-row") === -1;
    });
    var reasonOf = rows.map(function (r) {
      var next = r.nextElementSibling;
      return next && next.className.indexOf("reason-row") !== -1 ? next : null;
    });
    rows.forEach(function (r, i) { r._reason = reasonOf[i]; });
    rows.sort(function (a, b) {
      var va = cellValue(a, idx);
      var vb = cellValue(b, idx);
      if (va === null && vb === null) return 0;
      if (va === null) return 1;
      if (vb === null) return -1;
      if (typeof va === "number" && typeof vb === "number") return asc ? va - vb : vb - va;
      va = String(va);
      vb = String(vb);
      if (va < vb) return asc ? -1 : 1;
      if (va > vb) return asc ? 1 : -1;
      return 0;
    });
    for (var i = 0; i < rows.length; i++) {
      body.appendChild(rows[i]);
      if (rows[i]._reason) body.appendChild(rows[i]._reason);
    }
    for (var h = 0; h < headers.length; h++) headers[h].removeAttribute("data-sort-dir");
    headers[idx].setAttribute("data-sort-dir", asc ? "asc" : "desc");
  }

  for (var i = 0; i < headers.length; i++) {
    (function (idx) {
      headers[idx].tabIndex = 0;
      headers[idx].addEventListener("click", function () { sortBy(idx); });
      headers[idx].addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          sortBy(idx);
        }
      });
    })(i);
  }
})();
"""


def render_html(data: Dict[str, Any]) -> str:
    """返回完整 HTML 文档。data 为 build_report_data() 的报告字典。"""
    title = "litmus 测评报告 ({})".format(data.get("report_id") or "")
    sections = [
        _render_hero(data),
        _render_cards(data),
        _render_counts(data),
        _render_bars("按维度的通过率", _as_list(data.get("by_dimension")), _dimension_label),
        _render_bars("按难度的通过率", _as_list(data.get("by_difficulty")), _difficulty_label),
        _render_usage(data),
        _render_tasks(data),
        _render_interruptions(data),
        _render_env(data),
    ]
    body = "\n".join(section for section in sections if section)
    return "\n".join([
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>{}</title>".format(_e(title)),
        "<style>",
        _CSS.strip(),
        "</style>",
        "</head>",
        "<body>",
        '<main class="wrap">',
        body,
        "</main>",
        "<script>",
        _JS.strip(),
        "</script>",
        "</body>",
        "</html>",
        "",
    ])
