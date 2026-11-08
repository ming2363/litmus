"""校验码。只处理数字或约定字母表。"""


def luhn_ok(number):
    """校验含校验位的数字串。"""
    if not isinstance(number, str) or not number.isdigit() or len(number) < 2:
        return False
    total = 0
    reverse = number[::-1]
    for idx, ch in enumerate(reverse):
        digit = ord(ch) - 48
        if idx % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def luhn_check_digit(body):
    """给不含校验位的数字串补一位。"""
    if not isinstance(body, str) or not body.isdigit():
        raise ValueError(body)
    for candidate in "0123456789":
        if luhn_ok(body + candidate):
            return candidate
    raise RuntimeError("luhn")


def mod11_symbol(body, alphabet="0123456789X"):
    """从右往左权重 2.. 循环，余数映射到 alphabet。"""
    if not body or any(ch not in alphabet[:-1] for ch in body):
        raise ValueError(body)
    total = 0
    weight = 2
    for ch in reversed(body):
        total += (ord(ch) - 48) * weight
        weight += 1
        if weight > 7:
            weight = 2
    return alphabet[total % 11]


def mod97_ok(digits):
    """大整数模 97 等于 1。"""
    if not digits.isdigit():
        return False
    return int(digits) % 97 == 1
