"""纸质账单把元换成分。"""

from decimal import Decimal, ROUND_HALF_UP


def paper_cents(amount: Decimal) -> int:
    scaled = (amount * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(scaled)
