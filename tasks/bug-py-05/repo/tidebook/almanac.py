"""一周潮汐摘录。给调度台打印，不参与巷道归并。"""

from typing import List, Tuple

from tidebook.station import extrema, height_cm, station_names
from tidebook.window import open_windows

Excerpt = Tuple[str, int, int, int, str]


def day_bounds(day_index: int) -> Tuple[int, int]:
    if type(day_index) is not int:
        raise ValueError("日序号必须是整数")
    start = day_index * 1440
    return start, start + 1440


def daily_heights(station_id: str, day_index: int, step: int = 60) -> List[Tuple[int, int]]:
    start, end = day_bounds(day_index)
    rows = []
    cursor = start
    while cursor < end:
        rows.append((cursor, height_cm(station_id, cursor)))
        cursor += step
    return rows


def daily_turns(station_id: str, day_index: int) -> List[Tuple[int, int, str]]:
    start, end = day_bounds(day_index)
    return extrema(station_id, start, end, step=10)


def weekly_openings(
    station_id: str,
    draft_cm: int,
    margin_cm: int,
    first_day: int = 0,
    days: int = 7,
) -> List[Tuple[int, int]]:
    start, _end = day_bounds(first_day)
    finish = start + days * 1440
    return open_windows(station_id, start, finish, draft_cm, margin_cm, step=10)


def digest(station_id: str, day_index: int) -> str:
    turns = daily_turns(station_id, day_index)
    if not turns:
        return "{} 第 {} 日无转折".format(station_id, day_index)
    parts = []
    for minute, level, kind in turns:
        label = "高潮" if kind == "high" else "低潮"
        parts.append("{} {}cm@{}".format(label, level, minute))
    return "{} {}".format(station_id, "；".join(parts))


def all_stations(day_index: int) -> List[Excerpt]:
    rows: List[Excerpt] = []
    for station_id in station_names():
        for minute, level, kind in daily_turns(station_id, day_index):
            rows.append((station_id, day_index, minute, level, kind))
    return rows


def highest(day_index: int) -> Excerpt:
    rows = all_stations(day_index)
    if not rows:
        raise LookupError(day_index)
    return max(rows, key=lambda item: (item[3], item[0]))
