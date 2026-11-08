"""落库前附加校验符。"""


def attach_mod11_suffix(text):
    """权重 2 到 7 循环，余数 10 记为 X。"""
    total = 0
    weight = 2
    for ch in reversed(text):
        if "0" <= ch <= "9":
            digit = ord(ch) - 48
        else:
            digit = 0
        total += digit * weight
        weight += 1
        if weight > 7:
            weight = 2
    remain = total % 11
    suffix = "X" if remain == 10 else str(remain)
    return text + suffix


class TailStep(object):
    """落库步骤。"""

    def apply(self, text):
        return attach_mod11_suffix(text)
