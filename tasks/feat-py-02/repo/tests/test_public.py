import unittest

from src.db import (
    create_memory_db,
    seed_customers,
    seed_invoices,
    seed_plans,
    seed_refunds,
)
from src.reports import customer_net_spend, plan_revenue_summary


class TestPublic(unittest.TestCase):
    def setUp(self):
        self.conn = create_memory_db()
        seed_customers(
            self.conn,
            [
                (1, "Acme Corp", "east"),
                (2, "Beta Lab", "west"),
            ],
        )
        seed_plans(
            self.conn,
            [
                (1, "pro", 10000),
                (2, "starter", 3000),
            ],
        )
        seed_invoices(
            self.conn,
            [
                (101, 1, 1, "2026-01-05", 10000, "paid"),
                (102, 2, 2, "2026-01-12", 3000, "paid"),
                (103, 1, 1, "2026-01-20", 10000, "void"),
            ],
        )
        seed_refunds(
            self.conn,
            [
                (1, 101, "2026-01-18", 2500),
            ],
        )

    def tearDown(self):
        self.conn.close()

    def test_plan_revenue_summary(self):
        rows = plan_revenue_summary(self.conn)
        self.assertEqual(len(rows), 2)
        pro = rows[0]
        self.assertEqual(pro["plan_code"], "pro")
        self.assertEqual(pro["paid_invoice_count"], 1)
        self.assertEqual(pro["gross_cents"], 10000)
        self.assertEqual(pro["refund_cents"], 2500)
        self.assertEqual(pro["net_cents"], 7500)

    def test_customer_net_spend(self):
        rows = customer_net_spend(self.conn)
        self.assertEqual(rows[0]["net_cents"], 7500)
        self.assertEqual(rows[1]["net_cents"], 3000)


if __name__ == "__main__":
    unittest.main()
