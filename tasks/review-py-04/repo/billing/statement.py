"""把一期抄表收成结算单。"""

import logging
from decimal import Decimal
from typing import List, Sequence, Tuple

from billing.boxes import whole_boxes
from billing.charge import energy_fee
from billing.explain import explain_lines
from billing.minimum import minimum_fee
from billing.round_cents import yuan_to_cents
from protocol.reading import Reading

logger = logging.getLogger("billing.statement")


def build_statement(
    readings: Sequence[Reading],
    yuan_per_kwh: Decimal,
    floor_cents: int,
    box_count: Decimal,
) -> Tuple[int, int, List[str]]:
    """返回 (电费分, 整箱数, 说明行)。"""
    logger.info("statement readings=%s", len(readings))
    priced = []
    total = Decimal(0)
    for reading in readings:
        fee = energy_fee(reading, yuan_per_kwh)
        total += fee
        priced.append((reading, fee))
    lines = explain_lines(priced)
    cents = yuan_to_cents(total) + minimum_fee(len(readings), floor_cents)
    boxes = whole_boxes(box_count)
    logger.info("statement cents=%s boxes=%s", cents, boxes)
    return cents, boxes, lines
