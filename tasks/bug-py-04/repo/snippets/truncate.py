"""按码点个数截断字符串。组合字符和 emoji 会被切开。"""


def grapheme_length(text: str) -> int:
    _check_text(text)
    return len(text)


def truncate_graphemes(text: str, limit: int) -> str:
    """保留前 limit 个码点。"""
    _check_text(text)
    _check_limit(limit)
    return text[:limit]


def _check_text(text) -> None:
    if not isinstance(text, str):
        raise TypeError("text 必须是字符串")


def _check_limit(limit) -> None:
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit 必须是整数")
    if limit < 0:
        raise ValueError("limit 不能为负")
