"""靠泊延误沿同一泊位向后传递。时间是分钟。"""

from typing import Dict, List, Sequence, Tuple

from harborpipe.berth.plan import Booking


class DelayError(ValueError):
    """延误参数不合法。"""


def _ordered(bookings: Sequence[Booking], berth: str) -> List[Booking]:
    mine = [item for item in bookings if item.berth == berth]
    mine.sort(key=lambda item: (item.start, item.voyage))
    return mine


def propagate(bookings: Sequence[Booking], berth: str, voyage: str, extra: int) -> List[Tuple[str, int, int]]:
    """某航次多占 extra 分钟后，同泊位后续航次整体后移，但不提前。

    返回 (航次, 新开始, 新结束)。被点名的航次只拉长结束时刻。
    """
    if extra < 0:
        raise DelayError("延误不能为负")
    chain = _ordered(bookings, berth)
    if not any(item.voyage == voyage for item in chain):
        raise DelayError("这条泊位上没有该航次")
    cursor = 0
    seen = False
    result: List[Tuple[str, int, int]] = []
    for item in chain:
        start = item.start
        end = item.end
        if item.voyage == voyage:
            end += extra
            seen = True
        elif seen and start < cursor:
            shift = cursor - start
            start += shift
            end += shift
        if start < cursor:
            start = cursor
            if end < start:
                end = start
        result.append((item.voyage, start, end))
        cursor = end
    return result


def idle_gaps(rows: Sequence[Tuple[str, int, int]]) -> List[Tuple[int, int]]:
    """相邻航次之间空出来的半开间隔。"""
    gaps: List[Tuple[int, int]] = []
    previous_end = None
    for _voyage, start, end in rows:
        if previous_end is not None and start > previous_end:
            gaps.append((previous_end, start))
        previous_end = end
    return gaps


def crane_hours(rows: Sequence[Tuple[str, int, int]], cranes: int) -> int:
    """按占用分钟乘桥吊数，得到桥吊分钟。"""
    if cranes <= 0:
        raise DelayError("桥吊数必须为正")
    total = 0
    for _voyage, start, end in rows:
        if end < start:
            raise DelayError("结束早于开始")
        total += (end - start) * cranes
    return total


def summary(bookings: Sequence[Booking], slip: Dict[str, int]) -> Dict[str, List[Tuple[str, int, int]]]:
    """slip 是航次到额外分钟的映射。同一航次只计一次，按泊位分组传递。"""
    by_berth: Dict[str, List[Booking]] = {}
    for item in bookings:
        by_berth.setdefault(item.berth, []).append(item)
    out: Dict[str, List[Tuple[str, int, int]]] = {}
    for berth, chain in by_berth.items():
        # 同一泊位上可能有多段延误，按时间顺序逐段传递。
        current = [(item.voyage, item.start, item.end) for item in _ordered(chain, berth)]
        for voyage, _start, _end in list(current):
            extra = slip.get(voyage, 0)
            if extra <= 0:
                continue
            rebuilt = []
            for voyage_name, start, end in current:
                rebuilt.append(Booking(voyage_name, berth, start, end))
            current = propagate(rebuilt, berth, voyage, extra)
        out[berth] = current
    return out
