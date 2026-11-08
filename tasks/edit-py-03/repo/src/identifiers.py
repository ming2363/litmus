"""物流运单编号校验与提取模块。"""

import re
from typing import Dict, List, Optional

PARCEL_CODE_RE = re.compile(
    r"^(?P<site>[A-Z]{2})-(?P<year>20\d{2})-(?P<seq>\d{5})$"
)

INLINE_PARCEL_RE = re.compile(r"\b[A-Z]{2}-20\d{2}-\d{5}\b")


def parse_parcel_code(code: str) -> Optional[Dict[str, Optional[str]]]:
    """解析合法的物流单号并拆分字段；不合法时返回 None。"""
    if not isinstance(code, str):
        return None
    matched = PARCEL_CODE_RE.match(code)
    if matched is None:
        return None
    return {
        "site": matched.group("site"),
        "zone": None,
        "year": matched.group("year"),
        "seq": matched.group("seq"),
        "suffix": None,
    }


def is_valid_parcel_code(code: str) -> bool:
    """判断字符串是否为合法的物流运单编号。"""
    return parse_parcel_code(code) is not None


def extract_parcel_codes(text: str) -> List[str]:
    """按出现顺序从文本中提取合法物流单号列表。"""
    if not isinstance(text, str) or not text:
        return []
    return INLINE_PARCEL_RE.findall(text)
