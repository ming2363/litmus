"""导出给财务的行。amount_yuan 的单位是元。"""

from demurrage.calc import charge_cents


def export_row(start, end, hold_id):
    """增加了 hold_id。金额字段仍然是元。"""
    amount_yuan = charge_cents(start, end)
    return {"hold_id": hold_id, "amount_yuan": amount_yuan}
