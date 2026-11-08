"""车牌与箱号的形状检查，不是最终业务编码规则。"""


def normalize_plate(text):
    """去掉空格并大写。"""
    if not isinstance(text, str):
        raise TypeError("plate")
    return "".join(text.split()).upper()


def plate_shape_ok(text):
    """省份汉字 + 字母 + 5 或 6 位字母数字。只做形状检查。"""
    raw = normalize_plate(text)
    if len(raw) not in (7, 8):
        return False
    if not ("\u4e00" <= raw[0] <= "\u9fff"):
        return False
    if not ("A" <= raw[1] <= "Z"):
        return False
    return all(("A" <= ch <= "Z") or ch.isdigit() for ch in raw[2:])


def container_shape_ok(text):
    """4 字母 + 7 数字的箱号形状。"""
    raw = normalize_plate(text)
    if len(raw) != 11:
        return False
    if not raw[:4].isalpha():
        return False
    return raw[4:].isdigit()
