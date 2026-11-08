"""Claude Code 会话 JSONL 解析器（含子代理目录、按 requestId 去重）。"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from litmus.state import parse_iso
from litmus.usage import TokenBucket, UsageSummary, find_task_marker_in_text, safe_int


def _encode_project_path(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9-]", "-", str(path))


def _candidate_jsonl_files(root: Path, projects_root: Path) -> List[Path]:
    if not projects_root.is_dir():
        return []
    candidates: List[Path] = []
    seen: Set[Path] = set()
    for path_obj in (root, root.resolve()):
        encoded = _encode_project_path(path_obj)
        proj_dir = projects_root / encoded
        if proj_dir.is_dir():
            for p in sorted(proj_dir.rglob("*.jsonl")):
                rp = p.resolve()
                if rp not in seen:
                    seen.add(rp)
                    candidates.append(p)
    if candidates:
        return candidates
    return sorted(projects_root.rglob("*.jsonl"))


def _extract_text_for_markers(obj: Dict[str, Any]) -> str:
    parts: List[str] = []
    msg = obj.get("message")
    if isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    for k in ("content", "text"):
                        v = item.get(k)
                        if isinstance(v, str):
                            parts.append(v)
    tur = obj.get("toolUseResult")
    if isinstance(tur, str):
        parts.append(tur)
    elif isinstance(tur, dict):
        for k in ("stdout", "stderr", "content"):
            v = tur.get(k)
            if isinstance(v, str):
                parts.append(v)
    return "\n".join(parts)


def _ts_sort_key(raw_ts: Any, file_idx: int, line_idx: int) -> Tuple[float, int, int]:
    if isinstance(raw_ts, str) and raw_ts.strip():
        try:
            return parse_iso(raw_ts).timestamp(), file_idx, line_idx
        except ValueError:
            pass
    return 0.0, file_idx, line_idx


def collect_claude(
    marker: str,
    task_ids: Sequence[str],
    root: Path,
    base_dir: Optional[Path] = None,
) -> Optional[UsageSummary]:
    projects_root = base_dir if base_dir is not None else (Path.home() / ".claude" / "projects")
    all_files = _candidate_jsonl_files(root, projects_root)
    if not all_files:
        return None

    matched_files: Set[Path] = set()
    session_ids: Set[str] = set()

    for fpath in all_files:
        try:
            raw_text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if marker not in raw_text:
            continue
        matched_files.add(fpath)
        for line in raw_text.splitlines():
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and isinstance(obj.get("sessionId"), str):
                session_ids.add(obj["sessionId"])

    if not matched_files:
        return None

    # 将同 sessionId 的子代理 JSONL 一并纳入统计
    if session_ids:
        for fpath in all_files:
            if fpath in matched_files:
                continue
            try:
                with fpath.open("r", encoding="utf-8", errors="replace") as fh:
                    for _ in range(10):
                        line = fh.readline()
                        if not line:
                            break
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(obj, dict) and obj.get("sessionId") in session_ids:
                            matched_files.add(fpath)
                            break
            except OSError:
                continue

    events: List[Tuple[Tuple[float, int, int], Dict[str, Any]]] = []
    for file_idx, fpath in enumerate(sorted(matched_files)):
        try:
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_idx, raw_line in enumerate(lines):
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                obj = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            events.append((_ts_sort_key(obj.get("timestamp"), file_idx, line_idx), obj))

    events.sort(key=lambda pair: pair[0])

    current_task: Optional[str] = None
    dedup_requests: Dict[str, Tuple[Optional[str], str, Dict[str, Any]]] = {}
    anon_seq = 0

    for _, obj in events:
        text = _extract_text_for_markers(obj)
        if text:
            found_tid = find_task_marker_in_text(text, task_ids)
            if found_tid is not None:
                current_task = found_tid

        if obj.get("type") != "assistant":
            continue
        msg = obj.get("message")
        if not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
            continue
        model = str(msg.get("model") or obj.get("requestedModel") or "unknown")
        req_key = obj.get("requestId") or msg.get("id") or obj.get("uuid")
        if not isinstance(req_key, str) or not req_key:
            anon_seq += 1
            req_key = "__anon_{}".format(anon_seq)
        dedup_requests[req_key] = (current_task, model, msg["usage"])

    models: Dict[str, TokenBucket] = {}
    by_task: Dict[str, TokenBucket] = {}
    total = TokenBucket()

    for task_id, model, usage in dedup_requests.values():
        inp = safe_int(usage.get("input_tokens") or 0)
        out = safe_int(usage.get("output_tokens") or 0)
        c_read = safe_int(usage.get("cache_read_input_tokens") or 0)
        c_write = safe_int(usage.get("cache_creation_input_tokens") or 0)
        details = usage.get("output_tokens_details")
        reasoning = safe_int(details.get("thinking_tokens") or 0) if isinstance(details, dict) else 0

        total.add(inp, out, c_read, c_write, reasoning)
        models.setdefault(model, TokenBucket()).add(inp, out, c_read, c_write, reasoning)
        if task_id is not None:
            by_task.setdefault(task_id, TokenBucket()).add(inp, out, c_read, c_write, reasoning)

    return UsageSummary(
        collected=True,
        tool="claude",
        models=models,
        by_task=by_task,
        total=total,
    )
