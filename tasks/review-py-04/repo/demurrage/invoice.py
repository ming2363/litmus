"""发票金额用元。"""

from demurrage.calc import charge_cents


def invoice_yuan(start, end):
    """分转成元。"""
    return charge_cents(start, end) / 100.0
