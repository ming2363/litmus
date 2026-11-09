"""吃水建议。把潮汐可航窗口和巷道水深对上，结果不是占用计划。"""

from typing import List, Optional, Tuple

from tidebook.station import datum_cm, height_cm
from tidebook.window import open_windows
from wharfbook.lanes import YardMap, north_yard

Advice = Tuple[str, int, int, int]


def tide_depth_cm(station_id: str, minute: int) -> int:
    """潮高加上测站零点已经含在 height_cm 里，这里直接返回。"""
    return height_cm(station_id, minute)


def lane_margin(yard: YardMap, lane: str, station_id: str, minute: int, draft_cm: int) -> int:
    water = min(yard.depth_cm(lane), tide_depth_cm(station_id, minute))
    return water - draft_cm


def advise(
    station_id: str,
    draft_cm: int,
    start: int,
    end: int,
    yard: Optional[YardMap] = None,
    margin_cm: int = 50,
) -> List[Advice]:
    """每条水深够的巷道，给出第一段可航窗口。"""
    if draft_cm <= 0 or margin_cm < 0 or start >= end:
        raise ValueError("吃水建议的参数不合法")
    host = yard if yard is not None else north_yard()
    windows = open_windows(station_id, start, end, draft_cm, margin_cm, step=30)
    if not windows:
        return []
    opening = windows[0]
    rows: List[Advice] = []
    for code in host.codes():
        if host.depth_cm(code) < draft_cm + margin_cm:
            continue
        sample = tide_depth_cm(station_id, opening[0])
        if min(host.depth_cm(code), sample) < draft_cm + margin_cm:
            continue
        rows.append((code, opening[0], opening[1], host.depth_cm(code)))
    return rows


def datum_note(station_id: str) -> str:
    return "测站 {} 零点 {} 厘米".format(station_id, datum_cm(station_id))


def tightest(rows: List[Advice]) -> Optional[Advice]:
    if not rows:
        return None
    return min(rows, key=lambda item: (item[3], item[0]))
