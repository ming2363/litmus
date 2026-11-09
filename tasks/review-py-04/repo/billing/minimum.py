"""底度电费。"""


def minimum_fee(readings: int, floor_cents: int) -> int:
    if readings < 0 or floor_cents < 0:
        raise ValueError("底度参数不合法")
    if readings == 0:
        return 0
    return floor_cents
