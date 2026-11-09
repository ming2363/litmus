"""抄表导出成 CSV。"""

import logging
from decimal import Decimal
from typing import List, Sequence

from billing.charge import energy_fee
from billing.round_cents import yuan_to_cents
from export.order import sort_readings
from protocol.reading import Reading

logger = logging.getLogger("export.csv")


def _cell(value: object) -> str:
    text = str(value)
    if any(ch in text for ch in ",\"\n"):
        return '"' + text.replace('"', '""') + '"'
    return text


def to_csv(rows: Sequence[Reading], yuan_per_kwh: Decimal) -> str:
    ordered = sort_readings(rows)
    logger.info("csv rows=%s", len(ordered))
    lines: List[str] = ["meter_id,lane,taken_at,shift,amount_cents"]
    for reading in ordered:
        fee = energy_fee(reading, yuan_per_kwh)
        cents = yuan_to_cents(fee)
        minute = reading.taken_at % (24 * 60)
        if minute < 8 * 60:
            shift = "夜班"
        elif minute < 16 * 60:
            shift = "白班"
        else:
            shift = "中班"
        lines.append(
            ",".join(
                [
                    _cell(reading.meter_id),
                    _cell(reading.lane),
                    _cell(reading.taken_at),
                    _cell(shift),
                    _cell(cents),
                ]
            )
        )
    return "\n".join(lines) + "\n"
