"""金额：以分为整数，避免二进制浮点。"""


class MoneyError(ValueError):
    """金额不合法。"""


def parse_fen(text):
    """把「元」文本解析成分。允许最多两位小数。"""
    if not isinstance(text, str):
        raise MoneyError("text")
    raw = text.strip()
    sign = 1
    if raw.startswith("-"):
        sign = -1
        raw = raw[1:]
    if not raw or raw.count(".") > 1:
        raise MoneyError(text)
    whole, _, frac = raw.partition(".")
    if not whole.isdigit() or (frac and (not frac.isdigit() or len(frac) > 2)):
        raise MoneyError(text)
    frac = (frac + "00")[:2]
    return sign * (int(whole) * 100 + int(frac))


def format_fen(amount):
    """分格式化为元，固定两位小数。"""
    if not isinstance(amount, int):
        raise MoneyError("amount")
    sign = "-" if amount < 0 else ""
    value = abs(amount)
    return "{}{}.{:02d}".format(sign, value // 100, value % 100)


def allocate(total, weights):
    """按权重分配总额，余数分给当前小数部分最大的项。"""
    if not isinstance(total, int):
        raise MoneyError("total")
    if not weights or any((not isinstance(w, int) or w < 0) for w in weights):
        raise MoneyError("weights")
    base = sum(weights)
    if base == 0:
        if total == 0:
            return [0 for _ in weights]
        raise MoneyError("zero-weight")
    raw = [total * w for w in weights]
    shares = [item // base for item in raw]
    remain = total - sum(shares)
    order = sorted(range(len(weights)), key=lambda i: (-(raw[i] % base), i))
    step = 1 if remain > 0 else -1
    left = abs(remain)
    cursor = 0
    while left > 0:
        shares[order[cursor % len(order)]] += step
        left -= 1
        cursor += 1
    return shares


def tier_tax(amount_fen, brackets):
    """超额累进。brackets 为 (上限分或 None, 千分比) 且按上限升序。"""
    if amount_fen < 0:
        raise MoneyError("amount")
    tax = 0
    previous = 0
    for cap, rate in brackets:
        if cap is None:
            span = amount_fen - previous
        else:
            span = min(amount_fen, cap) - previous
        if span > 0:
            tax += span * rate // 1000
        if cap is None or amount_fen <= cap:
            break
        previous = cap
    return tax


def clamp_fee(amount, floor, ceiling):
    """把费用夹在闭区间内。"""
    if floor > ceiling:
        raise MoneyError("range")
    if amount < floor:
        return floor
    if amount > ceiling:
        return ceiling
    return amount
