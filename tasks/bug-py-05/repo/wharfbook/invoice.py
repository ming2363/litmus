"""在港停留费。停留窗口走 dwell，和巷道计划分开出账。"""

from typing import Sequence, Tuple

from wharfbook.dwell import billable_spans, open_spans

Span = Tuple[int, int]

# (不超过的分钟, 每分钟分)
STAY_BRACKETS: Tuple[Tuple[int, int], ...] = (
    (120, 15),
    (480, 12),
    (1440, 9),
    (10 ** 9, 7),
)


def _rate(minutes: int) -> int:
    for limit, rate in STAY_BRACKETS:
        if minutes <= limit:
            return rate
    return STAY_BRACKETS[-1][1]


def stay_cents(spans: Sequence[Span], closures: Sequence[Span]) -> int:
    kept = open_spans(spans, closures)
    minutes = sum(end - start for start, end in kept)
    if minutes == 0:
        return 0
    return minutes * _rate(minutes)


def gross_minutes(spans: Sequence[Span]) -> int:
    folded = billable_spans(spans)
    return sum(end - start for start, end in folded)


def statement(spans: Sequence[Span], closures: Sequence[Span]) -> str:
    gross = gross_minutes(spans)
    net_spans = open_spans(spans, closures)
    net = sum(end - start for start, end in net_spans)
    return "毛 {} 分钟，净 {} 分钟，费用 {} 分".format(gross, net, stay_cents(spans, closures))
