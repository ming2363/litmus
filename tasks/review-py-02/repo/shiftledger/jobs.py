"""夜间任务。"""

from shiftledger.query import where_shift


def nightly(conn, shift_id):
    """汇总一个班次，供凌晨任务调用。"""
    clause = where_shift(shift_id)
    sql = "SELECT id, amount FROM ledger_entry WHERE " + clause
    return conn.execute(sql).fetchall()
