import unittest

from src.models import (
    BundleRule,
    Coupon,
    OrderLine,
    OrderRequest,
    PromoRule,
    RefundItem,
)
from src.settlement_engine import (
    SettlementSession,
    reconcile_session_ledger,
    settle_order,
)


class TestPublic(unittest.TestCase):
    def test_settlement_with_discounts_and_shipping(self):
        req = OrderRequest(
            order_id="ORD-1001",
            region="CN_MAIN",
            member_tier="gold",
            lines=[
                OrderLine("SKU-A", "Keyboard", 6000, 2, weight_grams=600, tax_rate_bps=1000),
                OrderLine("SKU-B", "Mouse", 5000, 1, weight_grams=200, tax_rate_bps=1000),
            ],
            bundle_rules=[BundleRule("SKU-A", min_qty=2, discount_bps=1000)],
            promo_rule=PromoRule("P1", threshold_cents=12000, discount_cents=1500),
            coupon=Coupon("SAVE10", coupon_type="percent_off", discount_bps=1000, min_spend_cents=5000),
        )
        res = settle_order(req)
        self.assertEqual(res.gross_cents, 17000)
        self.assertEqual(res.bundle_discount_cents, 1200)
        self.assertEqual(res.member_discount_cents, 1580)
        self.assertEqual(res.promo_discount_cents, 1500)
        self.assertEqual(res.coupon_discount_cents, 1272)
        self.assertEqual(res.shipping_fee_cents, 0)
        self.assertTrue(res.shipping_waived)

    def test_sequential_refund_without_clawback_conserves_total(self):
        req = OrderRequest(
            order_id="ORD-1002",
            region="CN_MAIN",
            member_tier="none",
            lines=[
                OrderLine("SKU-A", "Chair", 10000, 3, tax_rate_bps=500),
                OrderLine("SKU-B", "Mat", 3000, 1, tax_rate_bps=500),
            ],
            promo_rule=PromoRule("P2", threshold_cents=20000, discount_cents=3000, clawback_on_breach=False),
        )
        res = settle_order(req)
        session = SettlementSession(res, req.promo_rule)
        q1 = session.apply_refund([RefundItem("SKU-A", 1)])
        q2 = session.apply_refund([RefundItem("SKU-A", 2), RefundItem("SKU-B", 1)])
        self.assertEqual(q1.promo_clawback_cents, 0)
        self.assertEqual(q2.promo_clawback_cents, 0)
        self.assertEqual(q1.total_refund_cents + q2.total_refund_cents, res.total_paid_cents - res.shipping_fee_cents)
        ledger = reconcile_session_ledger(session)
        self.assertEqual(ledger["goods_and_tax_discrepancy_cents"], 0)


if __name__ == "__main__":
    unittest.main()
