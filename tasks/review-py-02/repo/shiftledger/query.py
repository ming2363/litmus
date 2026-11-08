"""班次条件。"""


def where_shift(shift_id):
    """返回 SQL 片段和参数。片段只含占位符。"""
    if not isinstance(shift_id, str) or not shift_id.strip():
        raise ValueError("shift_id")
    return ("shift_id = ?", [shift_id.strip()])
