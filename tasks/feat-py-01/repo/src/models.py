"""记账工具数据模型与日期/金额工具函数。"""

from dataclasses import dataclass
from datetime import date

VALID_KINDS = ("income", "expense")


@dataclass(frozen=True)
class LedgerEntry:
    """单条收支明细。"""

    entry_id: str
    tx_date: date
    category: str
    kind: str
    amount_cents: int
    note: str = ""


def parse_iso_date(text: str) -> date:
    """解析日期字符串（起始实现未做严格 YYYY-MM-DD 格式约束）。"""
    if not isinstance(text, str):
        raise ValueError("日期必须是字符串: {!r}".format(text))
    return date.fromisoformat(text)


def format_cents(cents: int) -> str:
    """将整数分格式化为保留两位小数的元金额字符串。"""
    sign = "-" if cents < 0 else ""
    abs_val = abs(cents)
    return "{}{}.{:02d}".format(sign, abs_val // 100, abs_val % 100)
