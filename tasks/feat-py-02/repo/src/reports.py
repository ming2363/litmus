"""SaaS 订阅营收 SQL 报表模块。"""

import sqlite3
from typing import Any, Dict, List, Optional


def plan_revenue_summary(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """按套餐统计已支付发票总额与实收净额（按套餐 code 升序）。"""
    sql = """
    WITH refund_by_inv AS (
        SELECT invoice_id, COALESCE(SUM(amount_cents), 0) AS refunded_cents
        FROM refunds
        GROUP BY invoice_id
    )
    SELECT
        p.code AS plan_code,
        COUNT(CASE WHEN i.status = 'paid' THEN 1 END) AS paid_invoice_count,
        COALESCE(SUM(CASE WHEN i.status = 'paid' THEN i.amount_cents ELSE 0 END), 0) AS gross_cents,
        COALESCE(SUM(CASE WHEN i.status = 'paid' THEN COALESCE(r.refunded_cents, 0) ELSE 0 END), 0) AS refund_cents
    FROM plans p
    LEFT JOIN invoices i ON i.plan_id = p.id
    LEFT JOIN refund_by_inv r ON r.invoice_id = i.id
    GROUP BY p.id, p.code
    ORDER BY p.code ASC
    """
    rows = conn.execute(sql).fetchall()
    result: List[Dict[str, Any]] = []
    for row in rows:
        gross = int(row[2])
        refund = int(row[3])
        result.append(
            {
                "plan_code": str(row[0]),
                "paid_invoice_count": int(row[1]),
                "gross_cents": gross,
                "refund_cents": refund,
                "net_cents": gross - refund,
            }
        )
    return result


def customer_net_spend(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """按客户统计已支付总额、退款总额及净消费（按客户 id 升序）。"""
    sql = """
    WITH inv_agg AS (
        SELECT customer_id, COALESCE(SUM(amount_cents), 0) AS gross_cents
        FROM invoices
        WHERE status = 'paid'
        GROUP BY customer_id
    ),
    ref_agg AS (
        SELECT i.customer_id AS customer_id, COALESCE(SUM(r.amount_cents), 0) AS refund_cents
        FROM refunds r
        JOIN invoices i ON i.id = r.invoice_id
        WHERE i.status = 'paid'
        GROUP BY i.customer_id
    )
    SELECT
        c.id AS customer_id,
        c.name AS customer_name,
        c.region AS region,
        COALESCE(ia.gross_cents, 0) AS gross_cents,
        COALESCE(ra.refund_cents, 0) AS refund_cents
    FROM customers c
    LEFT JOIN inv_agg ia ON ia.customer_id = c.id
    LEFT JOIN ref_agg ra ON ra.customer_id = c.id
    ORDER BY c.id ASC
    """
    rows = conn.execute(sql).fetchall()
    out: List[Dict[str, Any]] = []
    for row in rows:
        gross = int(row[3])
        refund = int(row[4])
        out.append(
            {
                "customer_id": int(row[0]),
                "customer_name": str(row[1]),
                "region": str(row[2]),
                "gross_cents": gross,
                "refund_cents": refund,
                "net_cents": gross - refund,
            }
        )
    return out


def monthly_revenue_report(
    conn: sqlite3.Connection,
    start_month: str,
    end_month: str,
    region: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """按自然月汇总开票、退款、净收入及环比指标。"""
    raise NotImplementedError("monthly_revenue_report 尚未实现")
