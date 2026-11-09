"""按吃水从潮位曲线里切出可航窗口。切出来的窗口再交给分钟代数。"""

from typing import List, Tuple

from tidebook.span import fold_minutes
from tidebook.station import height_cm

Span = Tuple[int, int]


def open_windows(
    station_id: str,
    start: int,
    end: int,
    draft_cm: int,
    margin_cm: int,
    step: int = 10,
) -> List[Span]:
    """步长采样后，把潮高足够的连续分钟收成半开窗口。"""
    if step <= 0 or start >= end:
        raise ValueError("扫描参数不合法")
    if draft_cm <= 0 or margin_cm < 0:
        raise ValueError("吃水或富余水深不合法")
    need = draft_cm + margin_cm
    raw: List[Span] = []
    open_at = None
    cursor = start
    while cursor < end:
        if height_cm(station_id, cursor) >= need:
            if open_at is None:
                open_at = cursor
        elif open_at is not None:
            raw.append((open_at, cursor))
            open_at = None
        cursor += step
    if open_at is not None:
        raw.append((open_at, end))
    return fold_minutes(raw)


def first_opening(
    station_id: str,
    start: int,
    end: int,
    draft_cm: int,
    margin_cm: int,
    step: int = 10,
) -> Span:
    windows = open_windows(station_id, start, end, draft_cm, margin_cm, step)
    if not windows:
        raise LookupError(station_id)
    return windows[0]
