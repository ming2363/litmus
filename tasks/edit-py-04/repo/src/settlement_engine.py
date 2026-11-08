"""跨境电商订单结算、拆单预览与分段退货对账引擎。"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from src.models import (
    BundleRule,
    Coupon,
    OrderLine,
    OrderRequest,
    PromoRule,
    RefundItem,
    RefundQuote,
    SettledLine,
    SettlementResult,
)
from src.policies import (
    LOYALTY_RATE_PER_100_CENTS,
    MEMBER_DISCOUNT_BPS,
    REGION_SHIPPING_TABLE,
    allocate_proportional,
    round_half_up_bps,
)

VALID_COUPON_TYPES = ("percent_off", "voucher")


class SettlementError(ValueError):
    """结算或退货参数非法、数量越界或状态不合法时抛出。"""


@dataclass
class _LineRefundState:
    sku: str
    promo_eligible: bool
    remaining_qty: int
    remaining_after_member_cents: int
    remaining_promo_share_cents: int
    remaining_goods_net_cents: int
    remaining_tax_cents: int


def validate_order_request(request: OrderRequest) -> None:
    """校验下单请求基础字段合法性。"""
    if not request.order_id or not request.order_id.strip():
        raise SettlementError("order_id 不能为空")
    if request.region not in REGION_SHIPPING_TABLE:
        raise SettlementError("未知配送区域: {!r}".format(request.region))
    if request.member_tier not in MEMBER_DISCOUNT_BPS:
        raise SettlementError("未知会员等级: {!r}".format(request.member_tier))
    if not request.lines:
        raise SettlementError("订单明细不能为空")

    seen_skus = set()
    for line in request.lines:
        if not line.sku or not line.sku.strip():
            raise SettlementError("SKU 不能为空")
        if line.sku in seen_skus:
            raise SettlementError("订单内存在重复 SKU: {}".format(line.sku))
        seen_skus.add(line.sku)
        if line.unit_price_cents <= 0:
            raise SettlementError("商品单价必须大于 0: {}".format(line.sku))
        if line.quantity <= 0:
            raise SettlementError("商品数量必须大于 0: {}".format(line.sku))
        if line.weight_grams < 0:
            raise SettlementError("商品重量不能为负: {}".format(line.sku))
        if not (0 <= line.tax_rate_bps <= 5000):
            raise SettlementError("税率超出允许范围 [0, 5000]: {}".format(line.sku))

    if request.promo_rule is not None:
        if request.promo_rule.threshold_cents <= 0 or request.promo_rule.discount_cents < 0:
            raise SettlementError("满减规则配置非法")

    if request.coupon is not None:
        if request.coupon.coupon_type not in VALID_COUPON_TYPES:
            raise SettlementError("未知优惠券类型: {!r}".format(request.coupon.coupon_type))
        if request.coupon.coupon_type == "percent_off" and not (0 <= request.coupon.discount_bps <= 9000):
            raise SettlementError("折扣券比例非法")
        if request.coupon.coupon_type == "voucher" and request.coupon.amount_cents < 0:
            raise SettlementError("代金券面额不能为负")


def _compute_bundle_discounts(
    lines: List[OrderLine],
    bundle_rules: Iterable[BundleRule],
) -> Tuple[List[int], List[int]]:
    """按 SKU 匹配最优惠的满足门槛套装折扣。"""
    rules_by_sku: Dict[str, List[BundleRule]] = defaultdict(list)
    for rule in bundle_rules:
        if rule.min_qty > 0 and 0 <= rule.discount_bps <= 8000:
            rules_by_sku[rule.sku].append(rule)

    discounts: List[int] = []
    after_bundles: List[int] = []
    for line in lines:
        gross = line.unit_price_cents * line.quantity
        best_bps = 0
        for rule in rules_by_sku.get(line.sku, ()):
            if line.quantity >= rule.min_qty and rule.discount_bps > best_bps:
                best_bps = rule.discount_bps
        disc = round_half_up_bps(gross, best_bps)
        disc = min(disc, gross)
        discounts.append(disc)
        after_bundles.append(gross - disc)
    return discounts, after_bundles


def _compute_member_discounts(
    lines: List[OrderLine],
    after_bundle_list: List[int],
    member_tier: str,
) -> Tuple[List[int], List[int]]:
    """计算会员折扣并在参与会员折扣的明细行间精确分摊。"""
    tier_bps = MEMBER_DISCOUNT_BPS[member_tier]
    weights = [
        amt if line.member_eligible else 0
        for line, amt in zip(lines, after_bundle_list)
    ]
    eligible_sum = sum(weights)
    if tier_bps <= 0 or eligible_sum <= 0:
        return [0] * len(lines), list(after_bundle_list)

    total_member_disc = round_half_up_bps(eligible_sum, tier_bps)
    shares = allocate_proportional(total_member_disc, weights)
    after_member = [amt - share for amt, share in zip(after_bundle_list, shares)]
    return shares, after_member


def _allocate_store_promo(
    lines: List[OrderLine],
    after_member_list: List[int],
    promo_rule: Optional[PromoRule],
) -> Tuple[List[int], List[int]]:
    """在满足满减门槛时分摊全店满减优惠。"""
    n = len(lines)
    if promo_rule is None or promo_rule.discount_cents <= 0:
        return [0] * n, list(after_member_list)

    weights = [
        amt if line.promo_eligible else 0
        for line, amt in zip(lines, after_member_list)
    ]
    eligible_sum = sum(weights)
    if eligible_sum < promo_rule.threshold_cents:
        return [0] * n, list(after_member_list)

    promo_total = min(promo_rule.discount_cents, eligible_sum)
    shares = allocate_proportional(promo_total, weights)
    after_promo = [amt - share for amt, share in zip(after_member_list, shares)]
    return shares, after_promo


def _allocate_coupon_discount(
    after_promo_list: List[int],
    coupon: Optional[Coupon],
) -> Tuple[List[int], List[int]]:
    """根据优惠券类型与使用门槛计算各行分摊的券优惠金额。"""
    n = len(after_promo_list)
    if coupon is None:
        return [0] * n, list(after_promo_list)

    subtotal = sum(after_promo_list)
    if subtotal <= 0 or subtotal < coupon.min_spend_cents:
        return [0] * n, list(after_promo_list)

    if coupon.coupon_type == "percent_off":
        total_coupon = round_half_up_bps(subtotal, coupon.discount_bps)
    else:
        total_coupon = min(coupon.amount_cents, subtotal)

    if total_coupon <= 0:
        return [0] * n, list(after_promo_list)

    shares = allocate_proportional(total_coupon, after_promo_list)
    after_coupon = [amt - share for amt, share in zip(after_promo_list, shares)]
    return shares, after_coupon


def _evaluate_shipping(
    region: str,
    lines: List[OrderLine],
    after_promo_list: List[int],
    after_coupon_list: List[int],
    coupon: Optional[Coupon],
) -> Tuple[int, int, int, bool]:
    """核算订单基础运费、超重/偏远附加费与免基础运费状态。"""
    policy = REGION_SHIPPING_TABLE[region]
    physical_indices = [idx for idx, line in enumerate(lines) if not line.is_digital]
    if not physical_indices:
        return 0, 0, 0, True

    total_weight_grams = sum(
        lines[idx].weight_grams * lines[idx].quantity for idx in physical_indices
    )
    extra_weight = max(0, total_weight_grams - policy["free_overweight_grams"])
    extra_kg = (extra_weight + 999) // 1000 if extra_weight > 0 else 0
    surcharge = policy["remote_surcharge_cents"] + extra_kg * policy["per_extra_kg_cents"]

    use_after_coupon = coupon is not None and coupon.coupon_type == "percent_off"
    qualifying_physical = sum(
        after_coupon_list[idx] if use_after_coupon else after_promo_list[idx]
        for idx in physical_indices
    )
    waived = qualifying_physical >= policy["free_threshold_cents"]
    base_fee = 0 if waived else policy["base_cents"]
    return base_fee, surcharge, base_fee + surcharge, waived


def _compute_line_taxes(
    lines: List[OrderLine],
    after_coupon_list: List[int],
) -> List[int]:
    """按每行最终折后净额计税。"""
    return [
        round_half_up_bps(net_amt, line.tax_rate_bps)
        for line, net_amt in zip(lines, after_coupon_list)
    ]


def _build_warehouse_splits(lines: List[OrderLine]) -> Dict[str, Tuple[str, ...]]:
    """按履约仓库与数字交付分类生成预览拆单映射。"""
    buckets: Dict[str, List[str]] = defaultdict(list)
    for line in lines:
        key = "DIGITAL" if line.is_digital else line.warehouse
        buckets[key].append(line.sku)
    return {wh: tuple(sorted(skus)) for wh, skus in sorted(buckets.items())}


def _compute_loyalty_points(goods_after_coupon_cents: int, member_tier: str) -> int:
    """按实付商品净额估算会员积分收益。"""
    if goods_after_coupon_cents <= 0:
        return 0
    rate = LOYALTY_RATE_PER_100_CENTS[member_tier]
    return (goods_after_coupon_cents // 100) * rate


def settle_order(request: OrderRequest) -> SettlementResult:
    """执行完整下单结算流程并返回不可变结算快照。"""
    validate_order_request(request)

    lines = list(request.lines)
    gross_list = [line.unit_price_cents * line.quantity for line in lines]
    bundle_shares, after_bundle_list = _compute_bundle_discounts(lines, request.bundle_rules)
    member_shares, after_member_list = _compute_member_discounts(
        lines, after_bundle_list, request.member_tier
    )
    promo_shares, after_promo_list = _allocate_store_promo(
        lines, after_member_list, request.promo_rule
    )
    coupon_shares, after_coupon_list = _allocate_coupon_discount(
        after_promo_list, request.coupon
    )
    ship_base, ship_surcharge, ship_total, ship_waived = _evaluate_shipping(
        request.region, lines, after_promo_list, after_coupon_list, request.coupon
    )
    tax_list = _compute_line_taxes(lines, after_coupon_list)

    settled_lines: List[SettledLine] = []
    for idx, line in enumerate(lines):
        settled_lines.append(
            SettledLine(
                sku=line.sku,
                quantity=line.quantity,
                unit_price_cents=line.unit_price_cents,
                is_digital=line.is_digital,
                promo_eligible=line.promo_eligible,
                member_eligible=line.member_eligible,
                warehouse=line.warehouse,
                gross_cents=gross_list[idx],
                bundle_discount_cents=bundle_shares[idx],
                after_bundle_cents=after_bundle_list[idx],
                member_discount_cents=member_shares[idx],
                after_member_cents=after_member_list[idx],
                promo_share_cents=promo_shares[idx],
                after_promo_cents=after_promo_list[idx],
                coupon_share_cents=coupon_shares[idx],
                after_coupon_cents=after_coupon_list[idx],
                tax_cents=tax_list[idx],
            )
        )

    goods_net_total = sum(after_coupon_list)
    tax_total = sum(tax_list)
    return SettlementResult(
        order_id=request.order_id,
        region=request.region,
        member_tier=request.member_tier,
        lines=settled_lines,
        gross_cents=sum(gross_list),
        bundle_discount_cents=sum(bundle_shares),
        member_discount_cents=sum(member_shares),
        promo_discount_cents=sum(promo_shares),
        coupon_discount_cents=sum(coupon_shares),
        shipping_base_cents=ship_base,
        shipping_surcharge_cents=ship_surcharge,
        shipping_fee_cents=ship_total,
        shipping_waived=ship_waived,
        tax_cents=tax_total,
        total_paid_cents=goods_net_total + ship_total + tax_total,
        loyalty_points=_compute_loyalty_points(goods_net_total, request.member_tier),
        warehouse_splits=_build_warehouse_splits(lines),
    )


def estimate_precheck_eligible_subtotal(
    lines: List[OrderLine],
    bundle_rules: Iterable[BundleRule],
    member_tier: str,
) -> int:
    """下单前试算可参与全店满减的商品折后基准金额。"""
    _, after_bundle_list = _compute_bundle_discounts(lines, bundle_rules)
    _, after_member_list = _compute_member_discounts(lines, after_bundle_list, member_tier)
    return sum(
        amt for line, amt in zip(lines, after_member_list) if line.promo_eligible
    )


class SettlementSession:
    """支持多次分段退货与满减追回核算的有状态退货会话。"""

    def __init__(
        self,
        settlement: SettlementResult,
        promo_rule: Optional[PromoRule] = None,
    ) -> None:
        self._settlement = settlement
        self._promo_rule = promo_rule
        self._refund_seq = 0
        self._promo_clawed_back = False
        self._shipping_refunded = False
        self._history: List[RefundQuote] = []
        self._sku_order: List[str] = [line.sku for line in settlement.lines]
        self._line_states: Dict[str, _LineRefundState] = {
            line.sku: _LineRefundState(
                sku=line.sku,
                promo_eligible=line.promo_eligible,
                remaining_qty=line.quantity,
                remaining_after_member_cents=line.after_member_cents,
                remaining_promo_share_cents=line.promo_share_cents,
                remaining_goods_net_cents=line.after_coupon_cents,
                remaining_tax_cents=line.tax_cents,
            )
            for line in settlement.lines
        }

    @property
    def settlement(self) -> SettlementResult:
        return self._settlement

    @property
    def history(self) -> List[RefundQuote]:
        return list(self._history)

    @property
    def promo_clawed_back(self) -> bool:
        return self._promo_clawed_back

    def remaining_qty(self, sku: str) -> int:
        """查询指定 SKU 当前可退剩余数量。"""
        if sku not in self._line_states:
            raise SettlementError("未知 SKU: {}".format(sku))
        return self._line_states[sku].remaining_qty

    def remaining_total_goods_and_tax(self) -> int:
        """返回当前剩余未退商品与税款总额。"""
        return sum(
            state.remaining_goods_net_cents + state.remaining_tax_cents
            for state in self._line_states.values()
        )

    def _ordered_states(self) -> List[_LineRefundState]:
        return [self._line_states[sku] for sku in self._sku_order]

    def _validate_refund_batch(self, items: List[RefundItem]) -> Dict[str, int]:
        if not items:
            raise SettlementError("退货明细不能为空")
        aggregated: Dict[str, int] = defaultdict(int)
        for item in items:
            if item.sku not in self._line_states:
                raise SettlementError("订单中不存在 SKU: {}".format(item.sku))
            if item.quantity <= 0:
                raise SettlementError("退货数量必须大于 0: {}".format(item.sku))
            aggregated[item.sku] += item.quantity

        for sku, req_qty in aggregated.items():
            rem = self._line_states[sku].remaining_qty
            if req_qty > rem:
                raise SettlementError(
                    "SKU {} 退货数量 {} 超过剩余可退数量 {}".format(sku, req_qty, rem)
                )
        return dict(aggregated)

    def _reduce_line_state(self, sku: str, req_qty: int) -> Tuple[int, int]:
        """按剩余额精确扣减单行可退金额与税费（最后一件全额吸收尾差）。"""
        state = self._line_states[sku]
        rem_qty = state.remaining_qty
        if req_qty == rem_qty:
            goods_refund = state.remaining_goods_net_cents
            tax_refund = state.remaining_tax_cents
            member_released = state.remaining_after_member_cents
            promo_released = state.remaining_promo_share_cents
        else:
            goods_refund = (state.remaining_goods_net_cents * req_qty) // rem_qty
            tax_refund = (state.remaining_tax_cents * req_qty) // rem_qty
            member_released = (state.remaining_after_member_cents * req_qty) // rem_qty
            promo_released = (state.remaining_promo_share_cents * req_qty) // rem_qty

        state.remaining_qty -= req_qty
        state.remaining_goods_net_cents -= goods_refund
        state.remaining_tax_cents -= tax_refund
        state.remaining_after_member_cents -= member_released
        state.remaining_promo_share_cents -= promo_released
        return goods_refund, tax_refund

    def _evaluate_promo_clawback(self, refund_goods_cents: int) -> int:
        """在满足追回条件且尚未追回时，评估本次退货应追回的全店满减优惠。"""
        if self._promo_rule is None or not self._promo_rule.clawback_on_breach:
            return 0
        if self._promo_clawed_back or self._settlement.promo_discount_cents <= 0:
            return 0

        remaining_qualifying = sum(
            state.remaining_goods_net_cents + state.remaining_promo_share_cents
            for state in self._line_states.values()
        )
        if remaining_qualifying > self._promo_rule.threshold_cents:
            return 0

        unearned_promo = sum(
            state.remaining_promo_share_cents
            for state in self._line_states.values()
            if state.promo_eligible and state.remaining_qty > 0
        )
        self._promo_clawed_back = True
        if unearned_promo <= 0:
            return 0

        clawback_cents = min(refund_goods_cents, unearned_promo)
        weights = [
            state.remaining_promo_share_cents
            if (state.promo_eligible and state.remaining_qty > 0)
            else 0
            for state in self._ordered_states()
        ]
        restorations = allocate_proportional(clawback_cents, weights)
        for state, restore in zip(self._ordered_states(), restorations):
            if restore > 0:
                state.remaining_goods_net_cents += restore
                state.remaining_promo_share_cents = max(
                    0, state.remaining_promo_share_cents - restore
                )
        return clawback_cents

    def _maybe_refund_shipping(self, refund_shipping_if_all_returned: bool) -> int:
        """若订单已全量退完且允许退运费，则退回实付运费。"""
        if not refund_shipping_if_all_returned or self._shipping_refunded:
            return 0
        if any(state.remaining_qty > 0 for state in self._line_states.values()):
            return 0
        self._shipping_refunded = True
        return self._settlement.shipping_fee_cents

    def apply_refund(
        self,
        items: List[RefundItem],
        *,
        refund_shipping_if_all_returned: bool = False,
    ) -> RefundQuote:
        """执行一次退货并更新剩余状态，返回本次退货明细凭证。"""
        batch = self._validate_refund_batch(items)

        gross_goods_refund = 0
        tax_refund = 0
        for sku in self._sku_order:
            req_qty = batch.get(sku, 0)
            if req_qty > 0:
                g_ref, t_ref = self._reduce_line_state(sku, req_qty)
                gross_goods_refund += g_ref
                tax_refund += t_ref

        clawback = self._evaluate_promo_clawback(gross_goods_refund)
        items_refund = gross_goods_refund - clawback
        shipping_refund = self._maybe_refund_shipping(refund_shipping_if_all_returned)
        total_refund = items_refund + tax_refund + shipping_refund

        self._refund_seq += 1
        quote = RefundQuote(
            refund_seq=self._refund_seq,
            items_refund_cents=items_refund,
            promo_clawback_cents=clawback,
            tax_refund_cents=tax_refund,
            shipping_refund_cents=shipping_refund,
            total_refund_cents=total_refund,
            remaining_goods_and_tax_cents=self.remaining_total_goods_and_tax(),
        )
        self._history.append(quote)
        return quote


def reconcile_session_ledger(session: SettlementSession) -> Dict[str, int]:
    """校验历史累计退货、当前可退余额与原结算实付金额的对账差额。"""
    refunded_goods_and_tax = sum(
        q.items_refund_cents + q.tax_refund_cents for q in session.history
    )
    refunded_shipping = sum(q.shipping_refund_cents for q in session.history)
    remaining_gt = session.remaining_total_goods_and_tax()
    expected_gt = session.settlement.total_paid_cents - session.settlement.shipping_fee_cents
    return {
        "refunded_goods_and_tax_cents": refunded_goods_and_tax,
        "refunded_shipping_cents": refunded_shipping,
        "remaining_goods_and_tax_cents": remaining_gt,
        "expected_goods_and_tax_cents": expected_gt,
        "goods_and_tax_discrepancy_cents": (refunded_goods_and_tax + remaining_gt) - expected_gt,
        "total_clawback_cents": sum(q.promo_clawback_cents for q in session.history),
    }


def batch_settle_summary(requests: List[OrderRequest]) -> Dict[str, int]:
    """批量结算多笔订单并返回总金额、总优惠与总运费汇总。"""
    results = [settle_order(req) for req in requests]
    return {
        "order_count": len(results),
        "gross_cents": sum(r.gross_cents for r in results),
        "discount_cents": sum(
            r.bundle_discount_cents
            + r.member_discount_cents
            + r.promo_discount_cents
            + r.coupon_discount_cents
            for r in results
        ),
        "shipping_fee_cents": sum(r.shipping_fee_cents for r in results),
        "tax_cents": sum(r.tax_cents for r in results),
        "total_paid_cents": sum(r.total_paid_cents for r in results),
    }


def compare_promotion_candidates(
    base_request: OrderRequest,
    promo_candidates: List[Optional[PromoRule]],
    coupon_candidates: List[Optional[Coupon]],
) -> List[Dict[str, object]]:
    """对比多种满减与优惠券组合下的应付总额与省钱幅度，按实付从低到高排序。"""
    if not promo_candidates:
        promo_candidates = [base_request.promo_rule]
    if not coupon_candidates:
        coupon_candidates = [base_request.coupon]

    comparisons: List[Dict[str, object]] = []
    for promo in promo_candidates:
        for coupon in coupon_candidates:
            trial = OrderRequest(
                order_id=base_request.order_id,
                region=base_request.region,
                member_tier=base_request.member_tier,
                lines=base_request.lines,
                bundle_rules=base_request.bundle_rules,
                promo_rule=promo,
                coupon=coupon,
            )
            settled = settle_order(trial)
            comparisons.append(
                {
                    "promo_id": promo.rule_id if promo is not None else None,
                    "coupon_code": coupon.code if coupon is not None else None,
                    "total_paid_cents": settled.total_paid_cents,
                    "promo_discount_cents": settled.promo_discount_cents,
                    "coupon_discount_cents": settled.coupon_discount_cents,
                    "shipping_waived": settled.shipping_waived,
                }
            )
    comparisons.sort(key=lambda row: (int(row["total_paid_cents"]), str(row["promo_id"] or "")))
    return comparisons


def preview_region_shipping_quotes(request: OrderRequest) -> Dict[str, Dict[str, int]]:
    """预览同一购物车在不同配送区域下的基础运费、附加费与免邮差额。"""
    validate_order_request(request)
    lines = list(request.lines)
    _, after_bundle_list = _compute_bundle_discounts(lines, request.bundle_rules)
    _, after_member_list = _compute_member_discounts(lines, after_bundle_list, request.member_tier)
    _, after_promo_list = _allocate_store_promo(lines, after_member_list, request.promo_rule)
    _, after_coupon_list = _allocate_coupon_discount(after_promo_list, request.coupon)

    quotes: Dict[str, Dict[str, int]] = {}
    for region_name, policy in REGION_SHIPPING_TABLE.items():
        base_fee, surcharge, total_fee, waived = _evaluate_shipping(
            region_name, lines, after_promo_list, after_coupon_list, request.coupon
        )
        use_after_coupon = request.coupon is not None and request.coupon.coupon_type == "percent_off"
        qualifying = sum(
            after_coupon_list[i] if use_after_coupon else after_promo_list[i]
            for i, line in enumerate(lines)
            if not line.is_digital
        )
        gap_to_free = 0 if waived else max(0, policy["free_threshold_cents"] - qualifying)
        quotes[region_name] = {
            "base_cents": base_fee,
            "surcharge_cents": surcharge,
            "total_cents": total_fee,
            "gap_to_free_cents": gap_to_free,
        }
    return quotes

