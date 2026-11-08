"""航次号检查。"""

import re


# 航次号由字母数字段组成，段之间可以有连字符。
CALL_SIGN = re.compile(r"^(([A-Za-z0-9]+-?)+)+$")


def looks_like_call_sign(text):
    """空串不是航次号。"""
    if not isinstance(text, str) or not text:
        return False
    return CALL_SIGN.fullmatch(text) is not None


def lane_tail(note):
    """取连字符后面的那段。note 可能没有连字符。"""
    parts = [part for part in note.split("-") if part]
    return parts[1]


def describe(note):
    """同时给出是否像航次号，以及后段。"""
    return {"ok": looks_like_call_sign(note), "tail": lane_tail(note)}
