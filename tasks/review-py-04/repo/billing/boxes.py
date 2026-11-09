"""箱数取整。"""

from decimal import Decimal


def whole_boxes(raw: Decimal) -> int:
    if raw < 0:
        raise ValueError("箱数不能为负")
    return int(raw)
