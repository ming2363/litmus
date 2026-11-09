"""引航费按潮汐窗口的分钟数分档，窗口先走分钟代数。"""

from typing import List, Sequence, Tuple

from tidebook.span import cut_minutes, fold_minutes

Span = Tuple[int, int]

# (不超过的分钟数, 每分钟分)
BRACKETS: Tuple[Tuple[int, int], ...] = (
    (60, 80),
    (180, 70),
    (360, 60),
    (720, 50),
    (10 ** 9, 40),
)


def billable_minutes(windows: Sequence[Span], closures: Sequence[Span]) -> int:
    kept = cut_minutes(windows, closures)
    total = 0
    for start, end in kept:
        total += end - start
    return total


def _rate(minutes: int) -> int:
    if minutes < 0:
        raise ValueError("计费分钟不能为负")
    for limit, rate in BRACKETS:
        if minutes <= limit:
            return rate
    return BRACKETS[-1][1]


def pilotage_cents(windows: Sequence[Span], closures: Sequence[Span], pilots: int) -> int:
    """引航费，整数分。引航员人数按人叠加，不按窗口拆开重算档。"""
    if type(pilots) is not int or pilots <= 0:
        raise ValueError("引航员人数必须是正整数")
    minutes = billable_minutes(windows, closures)
    return minutes * _rate(minutes) * pilots


def explain(windows: Sequence[Span], closures: Sequence[Span]) -> List[str]:
    folded = fold_minutes(windows)
    kept = cut_minutes(windows, closures)
    lines = ["折叠后 {} 段".format(len(folded))]
    for start, end in kept:
        lines.append("{}-{} 共 {} 分钟".format(start, end, end - start))
    return lines
