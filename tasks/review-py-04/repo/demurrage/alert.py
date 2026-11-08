"""超过 500 元就告警。"""

from demurrage.calc import charge_cents


def should_alert(start, end):
    """阈值是 500 元。"""
    return charge_cents(start, end) > 500
