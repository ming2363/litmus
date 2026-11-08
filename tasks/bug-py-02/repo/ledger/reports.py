"""门店与日期两个口径的销售汇总。"""

import sqlite3
from typing import Dict, List


_STORE_SQL = """
SELECT
    s.id AS store_id,
    s.name AS store_name,
    s.region AS region,
    COUNT(o.amount_cents) AS paid_orders,
    SUM(o.amount_cents) AS paid_amount_cents,
    SUM(CASE WHEN o.status = 'refunded' THEN 1 ELSE 0 END) AS refunded_orders
FROM stores s
LEFT JOIN orders o ON s.id = o.store_id
WHERE o.status = 'paid'
GROUP BY s.id, s.name, s.region
ORDER BY s.id
"""

_DAILY_SQL = """
SELECT COALESCE(SUM(COALESCE(amount_cents, 0)), 0) AS total_cents
FROM orders
WHERE status = 'paid' AND ordered_on = ?
"""


def _as_int(value):
    if value is None:
        return None
    return int(value)


def store_paid_report(conn: sqlite3.Connection) -> List[Dict]:
    """按门店汇总已支付订单。没有支付记录的门店不会出现在结果里。"""
    rows = []
    for record in conn.execute(_STORE_SQL):
        rows.append(
            {
                "store_id": int(record["store_id"]),
                "store_name": record["store_name"],
                "region": record["region"],
                "paid_orders": _as_int(record["paid_orders"]),
                "paid_amount_cents": _as_int(record["paid_amount_cents"]),
                "refunded_orders": _as_int(record["refunded_orders"]),
            }
        )
    return rows


def daily_paid_total(conn: sqlite3.Connection, day: str) -> int:
    """某一天已支付金额合计。空金额按 0，没有订单时也是 0。"""
    row = conn.execute(_DAILY_SQL, (day,)).fetchone()
    total = row["total_cents"] if isinstance(row, sqlite3.Row) else row[0]
    return int(total)


def store_names(conn: sqlite3.Connection) -> List[str]:
    return [row[0] for row in conn.execute("SELECT name FROM stores ORDER BY id")]
