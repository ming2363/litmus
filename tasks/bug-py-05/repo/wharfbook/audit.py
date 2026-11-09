"""把一版计划收成调度台能贴进值班日志的文本。"""

from typing import List, Sequence, Tuple

Hold = Tuple[int, int, str]


def _clock(minute: int) -> str:
    sign = "-" if minute < 0 else ""
    absolute = abs(minute)
    day, rest = divmod(absolute, 1440)
    hour, mint = divmod(rest, 60)
    return "{}D{} {:02d}:{:02d}".format(sign, day, hour, mint)


def lines_of(plan: Sequence[Hold]) -> List[str]:
    rows = []
    for index, (start, end, lane) in enumerate(plan, start=1):
        rows.append(
            "{:02d} 巷道 {}  {} -> {}  ({} 分钟)".format(
                index, lane, _clock(start), _clock(end), end - start
            )
        )
    return rows


def digest(plan: Sequence[Hold]) -> str:
    if not plan:
        return "空计划"
    lanes = sorted({lane for _start, _end, lane in plan})
    minutes = sum(end - start for start, end, _lane in plan)
    return "巷道 {} 段 {} 段，合计 {} 分钟".format("、".join(lanes), len(plan), minutes)


def by_lane(plan: Sequence[Hold]) -> List[Tuple[str, int]]:
    totals = {}
    for start, end, lane in plan:
        totals[lane] = totals.get(lane, 0) + (end - start)
    return sorted(totals.items())
