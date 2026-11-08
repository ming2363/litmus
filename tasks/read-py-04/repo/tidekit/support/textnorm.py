"""文本归一。不承担业务字段的落库转换。"""


_FULLWIDTH = {i: i - 0xFEE0 for i in range(0xFF01, 0xFF5F)}
_FULLWIDTH[0x3000] = 0x20


def fold_width(text):
    """全角 ASCII 折成半角。"""
    if not isinstance(text, str):
        raise TypeError("text")
    return text.translate(_FULLWIDTH)


def squeeze_spaces(text):
    """连续空白收成一个空格，并去掉两端。"""
    return " ".join(fold_width(text).split())


def digits_only(text):
    """保留十进制数字。"""
    return "".join(ch for ch in fold_width(text) if "0" <= ch <= "9")


def prefix_match(candidates, query, limit=10):
    """前缀匹配，按字典序，最多 limit 条。"""
    if limit < 0:
        raise ValueError("limit")
    folded = squeeze_spaces(query).lower()
    hits = []
    for item in candidates:
        if squeeze_spaces(item).lower().startswith(folded):
            hits.append(item)
    hits.sort()
    return hits[:limit]
