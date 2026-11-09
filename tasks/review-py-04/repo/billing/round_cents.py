"""把元换算成整数分。"""

from decimal import Decimal


def yuan_to_cents(amount: Decimal) -> int:
    quantized = amount.quantize(Decimal("0.01"))
    return int(quantized * Decimal(100))
