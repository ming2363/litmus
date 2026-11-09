"""Codex 会话 JSONL 解析器（主解析 event_msg:token_count，按累计差值去重）。"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from litmus.usage import TokenBucket, UsageSummary, find_task_marker_in_text, safe_int


def _extract_codex_text(obj: Dict[str, Any]) -> str:
    t = obj.get("type")
    pl = obj.get("payload")
    if not isinstance(pl, dict):
        return ""
    texts: List[str] = []
    if t == "response_item":
        out = pl.get("output")
        if isinstance(out, str):
            texts.append(out)
        content = pl.get("content")
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and isinstance(c.get("text"), str):
                    texts.append(c["text"])
        elif isinstance(content, str):
            texts.append(content)
    elif t == "event_msg":
        msg = pl.get("message")
        if isinstance(msg, str):
            texts.append(msg)
    return "\n".join(texts)


_CODEX_KEYS: Tuple[str, ...] = (
    "input_tokens",
    "output_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "reasoning_output_tokens",
)


def _compute_delta(
    tot: Optional[Dict[str, Any]],
    last: Optional[Dict[str, Any]],
    prev_tot: Optional[Dict[str, int]],
) -> Tuple[Optional[Dict[str, int]], Optional[Dict[str, int]]]:
    if isinstance(tot, dict):
        cur_tot = {k: safe_int(tot.get(k) or 0) for k in _CODEX_KEYS}
        if prev_tot is not None:
            if cur_tot == prev_tot:
                return None, prev_tot
            if all(cur_tot[k] >= prev_tot[k] for k in _CODEX_KEYS):
                delta = {k: cur_tot[k] - prev_tot[k] for k in _CODEX_KEYS}
                return delta, cur_tot
        if isinstance(last, dict):
            return {k: safe_int(last.get(k) or 0) for k in _CODEX_KEYS}, cur_tot
        return cur_tot, cur_tot

    if isinstance(last, dict):
        return {k: safe_int(last.get(k) or 0) for k in _CODEX_KEYS}, prev_tot
    return None, prev_tot


def collect_codex(
    marker: str,
    task_ids: Sequence[str],
    base_dir: Optional[Path] = None,
) -> Optional[UsageSummary]:
    sessions_root = base_dir if base_dir is not None else (Path.home() / ".codex" / "sessions")
    if not sessions_root.is_dir():
        return None

    matched_files: List[Path] = []
    for fpath in sorted(sessions_root.rglob("rollout-*.jsonl")):
        try:
            raw_text = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if marker in raw_text:
            matched_files.append(fpath)

    if not matched_files:
        return None

    models: Dict[str, TokenBucket] = {}
    by_task: Dict[str, TokenBucket] = {}
    total = TokenBucket()

    for fpath in matched_files:
        current_model = "unknown"
        current_task: Optional[str] = None
        prev_tot: Optional[Dict[str, int]] = None

        try:
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        for raw_line in lines:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            try:
                obj = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue

            t = obj.get("type")
            pl = obj.get("payload")
            if not isinstance(pl, dict):
                continue

            if t == "turn_context" and isinstance(pl.get("model"), str) and pl["model"].strip():
                current_model = pl["model"].strip()
            elif t == "session_meta" and current_model == "unknown" and isinstance(pl.get("model"), str):
                current_model = pl["model"].strip()

            text = _extract_codex_text(obj)
            if text:
                found_tid = find_task_marker_in_text(text, task_ids)
                if found_tid is not None:
                    current_task = found_tid

            if t == "event_msg" and pl.get("type") == "token_count":
                info = pl.get("info")
                if not isinstance(info, dict):
                    continue
                delta, prev_tot = _compute_delta(
                    info.get("total_token_usage"),
                    info.get("last_token_usage"),
                    prev_tot,
                )
                if delta is None:
                    continue
                raw_inp = delta["input_tokens"]
                c_read = delta["cached_input_tokens"]
                # 统一口径：OpenAI 的 input_tokens 包含 cached_input_tokens，记入时扣除缓存命中
                inp = max(0, raw_inp - c_read)
                out = delta["output_tokens"]
                c_write = delta["cache_write_input_tokens"]
                reasoning = delta["reasoning_output_tokens"]

                total.add(inp, out, c_read, c_write, reasoning)
                models.setdefault(current_model, TokenBucket()).add(inp, out, c_read, c_write, reasoning)
                if current_task is not None:
                    by_task.setdefault(current_task, TokenBucket()).add(inp, out, c_read, c_write, reasoning)

    return UsageSummary(
        collected=True,
        tool="codex",
        models=models,
        by_task=by_task,
        total=total,
    )
