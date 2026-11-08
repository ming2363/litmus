import unittest

from ledger.formatters import format_report
from ledger.reports import daily_paid_total, store_paid_report
from ledger.schema import add_order, add_store, connect, init_db


def _happy(conn):
    init_db(conn)
    add_store(conn, 1, "北门", "east")
    add_store(conn, 2, "南门", "west")
    add_order(conn, 10, 1, "paid", 500, "2026-04-01")
    add_order(conn, 11, 1, "paid", 1500, "2026-04-01")
    add_order(conn, 12, 2, "paid", 800, "2026-04-02")


class TestPublic(unittest.TestCase):
    def test_paid_stores_with_amounts(self):
        conn = connect()
        _happy(conn)
        rows = store_paid_report(conn)
        self.assertEqual(
            rows,
            [
                {
                    "store_id": 1,
                    "store_name": "北门",
                    "region": "east",
                    "paid_orders": 2,
                    "paid_amount_cents": 2000,
                    "refunded_orders": 0,
                },
                {
                    "store_id": 2,
                    "store_name": "南门",
                    "region": "west",
                    "paid_orders": 1,
                    "paid_amount_cents": 800,
                    "refunded_orders": 0,
                },
            ],
        )

    def test_daily_total_ignores_null_and_other_days(self):
        conn = connect()
        init_db(conn)
        add_store(conn, 1, "北门", "east")
        add_order(conn, 1, 1, "paid", 100, "2026-04-01")
        add_order(conn, 2, 1, "paid", None, "2026-04-01")
        add_order(conn, 3, 1, "paid", 50, "2026-04-02")
        add_order(conn, 4, 1, "pending", 999, "2026-04-01")
        self.assertEqual(daily_paid_total(conn, "2026-04-01"), 100)
        self.assertEqual(daily_paid_total(conn, "2026-04-03"), 0)

    def test_format_contains_store_name(self):
        conn = connect()
        _happy(conn)
        text = format_report(store_paid_report(conn))
        self.assertIn("北门", text)
        self.assertIn("2000", text)

    def test_empty_database(self):
        conn = connect()
        init_db(conn)
        self.assertEqual(store_paid_report(conn), [])
        self.assertEqual(daily_paid_total(conn, "2026-04-01"), 0)
