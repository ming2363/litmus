"""白班汇总，已改成占位符。"""

from shiftledger.query import where_shift


def daily(conn, shift_id):
    """汇总一个班次。"""
    clause, params = where_shift(shift_id)
    sql = "SELECT id, amount FROM ledger_entry WHERE " + clause
    return conn.execute(sql, params).fetchall()
