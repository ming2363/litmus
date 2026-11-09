"""把每条抄表展开成可读的一行。"""

from decimal import Decimal
from typing import List, Sequence, Tuple

from protocol.reading import Reading

Priced = Tuple[Reading, Decimal]


def _lane_label(lane: str) -> str:
    text = lane.strip()
    if not text:
        return "-"
    return text


def _meter_label(meter_id: str) -> str:
    text = meter_id.strip()
    if len(text) <= 4:
        return text
    return text[:2] + "*" + text[-2:]


def _shift_label(taken_at: int) -> str:
    minute = taken_at % (24 * 60)
    if minute < 8 * 60:
        return "夜班"
    if minute < 16 * 60:
        return "白班"
    return "中班"


def explain_one(reading: Reading, fee: Decimal) -> str:
    return "{} {} {} {} {}".format(
        _meter_label(reading.meter_id),
        _lane_label(reading.lane),
        _shift_label(reading.taken_at),
        reading.energy,
        fee,
    )


def explain_lines(priced: Sequence[Priced]) -> List[str]:
    lines = [explain_one(reading, fee) for reading, fee in priced]
    if not lines:
        lines.append("本期没有抄表")
    return lines


def join_explain(priced: Sequence[Priced]) -> str:
    return "\n".join(explain_lines(priced))
