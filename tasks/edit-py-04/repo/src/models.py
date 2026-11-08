"""结算与退货引擎领域数据模型。"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class OrderLine:
    """下单明细行。"""

    sku: str
    title: str
    unit_price_cents: int
    quantity: int
    is_digital: bool = False
    weight_grams: int = 0
    promo_eligible: bool = True
    member_eligible: bool = True
    tax_rate_bps: int = 0
    warehouse: str = "WH-EAST"


@dataclass(frozen=True)
class BundleRule:
    """同 SKU 多件阶梯捆绑折扣规则。"""

    sku: str
    min_qty: int
    discount_bps: int


@dataclass(frozen=True)
class PromoRule:
    """全店满减活动规则。"""

    rule_id: str
    threshold_cents: int
    discount_cents: int
    clawback_on_breach: bool = False


@dataclass(frozen=True)
class Coupon:
    """订单优惠券（折扣券或代金券）。"""

    code: str
    coupon_type: str  # "percent_off" 或 "voucher"
    discount_bps: int = 0
    amount_cents: int = 0
    min_spend_cents: int = 0


@dataclass(frozen=True)
class OrderRequest:
    """完整订单结算请求。"""

    order_id: str
    region: str  # "CN_MAIN" / "CN_REMOTE" / "INTL"
    member_tier: str  # "none" / "silver" / "gold"
    lines: List[OrderLine]
    bundle_rules: List[BundleRule] = field(default_factory=list)
    promo_rule: Optional[PromoRule] = None
    coupon: Optional[Coupon] = None


@dataclass(frozen=True)
class SettledLine:
    """结算后的单行价格与税费明细。"""

    sku: str
    quantity: int
    unit_price_cents: int
    is_digital: bool
    promo_eligible: bool
    member_eligible: bool
    warehouse: str
    gross_cents: int
    bundle_discount_cents: int
    after_bundle_cents: int
    member_discount_cents: int
    after_member_cents: int
    promo_share_cents: int
    after_promo_cents: int
    coupon_share_cents: int
    after_coupon_cents: int
    tax_cents: int


@dataclass(frozen=True)
class SettlementResult:
    """订单整体结算快照。"""

    order_id: str
    region: str
    member_tier: str
    lines: List[SettledLine]
    gross_cents: int
    bundle_discount_cents: int
    member_discount_cents: int
    promo_discount_cents: int
    coupon_discount_cents: int
    shipping_base_cents: int
    shipping_surcharge_cents: int
    shipping_fee_cents: int
    shipping_waived: bool
    tax_cents: int
    total_paid_cents: int
    loyalty_points: int
    warehouse_splits: Dict[str, Tuple[str, ...]]


@dataclass(frozen=True)
class RefundItem:
    """退货请求项。"""

    sku: str
    quantity: int


@dataclass(frozen=True)
class RefundQuote:
    """单次分段退货核算结果。"""

    refund_seq: int
    items_refund_cents: int
    promo_clawback_cents: int
    tax_refund_cents: int
    shipping_refund_cents: int
    total_refund_cents: int
    remaining_goods_and_tax_cents: int
