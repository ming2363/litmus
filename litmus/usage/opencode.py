"""OpenCode 本地 SQLite 会话解析器（只读 URI 打开）。"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from litmus.usage import TokenBucket, UsageSummary, find_task_marker_in_text, safe_int


def _extract_part_text(data: Dict[str, Any]) -> str:
    ptype = data.get("type")
    if ptype == "tool":
        state = data.get("state")
        if isinstance(state, dict) and isinstance(state.get("output"), str):
            return state["output"]
    if ptype == "text" and isinstance(data.get("text"), str):
        return data["text"]
    return ""


def collect_opencode(
    marker: str,
    task_ids: Sequence[str],
    db_path: Optional[Path] = None,
) -> Optional[UsageSummary]:
    target = db_path if db_path is not None else (Path.home() / ".local" / "share" / "opencode" / "opencode.db")
    if not target.is_file():
        return None

    uri = "file:{}?mode=ro".format(target.resolve())
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(uri, uri=True)
        cur = conn.cursor()

        seed_rows = cur.execute(
            "SELECT DISTINCT session_id FROM part WHERE data LIKE ?",
            ("%{}%".format(marker),),
        ).fetchall()
        session_ids: Set[str] = {str(r[0]) for r in seed_rows if r and r[0]}
        if not session_ids:
            return None

        # 包含子会话（parent_id 指向主会话）
        frontier = list(session_ids)
        while frontier:
            placeholders = ",".join("?" for _ in frontier)
            children = cur.execute(
                "SELECT id FROM session WHERE parent_id IN ({})".format(placeholders),
                frontier,
            ).fetchall()
            new_ids = [str(r[0]) for r in children if r and r[0] and str(r[0]) not in session_ids]
            session_ids.update(new_ids)
            frontier = new_ids

        sid_list = sorted(session_ids)
        placeholders = ",".join("?" for _ in sid_list)

        msg_rows = cur.execute(
            "SELECT id, time_created, data FROM message WHERE session_id IN ({})".format(placeholders),
            sid_list,
        ).fetchall()
        part_rows = cur.execute(
            "SELECT id, time_created, data FROM part WHERE session_id IN ({})".format(placeholders),
            sid_list,
        ).fetchall()
    except sqlite3.Error:
        return None
    finally:
        if conn is not None:
            conn.close()

    # 按 time_created 排序交织 message(kind=0) 与 part(kind=1)
    timeline: List[Tuple[int, int, str, Dict[str, Any]]] = []
    for mid, t_created, raw_data in msg_rows:
        try:
            obj = json.loads(raw_data)
        except (TypeError, json.JSONDecodeError):
            continue
        if isinstance(obj, dict):
            timeline.append((safe_int(t_created), 0, str(mid), obj))

    for pid, t_created, raw_data in part_rows:
        try:
            obj = json.loads(raw_data)
        except (TypeError, json.JSONDecodeError):
            continue
        if isinstance(obj, dict):
            timeline.append((safe_int(t_created), 1, str(pid), obj))

    timeline.sort(key=lambda item: (item[0], item[1], item[2]))

    current_task: Optional[str] = None
    models: Dict[str, TokenBucket] = {}
    by_task: Dict[str, TokenBucket] = {}
    total = TokenBucket()

    for _, kind, _, data in timeline:
        if kind == 1:
            text = _extract_part_text(data)
            if text:
                found_tid = find_task_marker_in_text(text, task_ids)
                if found_tid is not None:
                    current_task = found_tid
            continue

        if data.get("role") != "assistant":
            continue
        tokens = data.get("tokens")
        if not isinstance(tokens, dict):
            continue

        model = data.get("modelID")
        if not isinstance(model, str) or not model.strip():
            model_obj = data.get("model")
            model = model_obj.get("modelID") if isinstance(model_obj, dict) else "unknown"
        model_id = str(model or "unknown")

        cache = tokens.get("cache")
        if not isinstance(cache, dict):
            cache = {}
        inp = safe_int(tokens.get("input") or 0)
        out = safe_int(tokens.get("output") or 0)
        reasoning = safe_int(tokens.get("reasoning") or 0)
        c_read = safe_int(cache.get("read") or 0)
        c_write = safe_int(cache.get("write") or 0)

        total.add(inp, out, c_read, c_write, reasoning)
        models.setdefault(model_id, TokenBucket()).add(inp, out, c_read, c_write, reasoning)
        if current_task is not None:
            by_task.setdefault(current_task, TokenBucket()).add(inp, out, c_read, c_write, reasoning)

    return UsageSummary(
        collected=True,
        tool="opencode",
        models=models,
        by_task=by_task,
        total=total,
    )
