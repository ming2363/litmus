"""抄表协议。"""

from decimal import Decimal
from typing import NamedTuple


class Reading(NamedTuple):
    meter_id: str
    lane: str
    taken_at: int
    energy: Decimal
    voltage: Decimal


def reading_from_watt_hours(
    meter_id: str,
    lane: str,
    taken_at: int,
    watt_hours: int,
    voltage: str,
) -> Reading:
    if type(watt_hours) is not int or watt_hours < 0:
        raise ValueError("瓦时不合法")
    if type(taken_at) is not int or taken_at < 0:
        raise ValueError("抄表时间不合法")
    if not str(meter_id).strip() or not str(lane).strip():
        raise ValueError("表号或巷道为空")
    energy = Decimal(watt_hours) / Decimal(1000)
    return Reading(str(meter_id).strip(), str(lane).strip(), taken_at, energy, Decimal(voltage))
