"""把订单预占、赠品、优惠券和收费串成一次结算。"""

from warehouse.errors import CouponError, PaymentDeclined
from warehouse.holds import HoldSession
from warehouse.models import Order, OrderLine, Receipt
from warehouse.promotions import attach_gift
from warehouse.stock import StockBook


_ACCEPTED_COUPONS = {None, "", "SAVE10"}


def checkout(book: StockBook, gateway, order: Order) -> Receipt:
    """收费成功才把预占转成已售。"""
    _validate_lines(order.lines)
    session = HoldSession(book)
    try:
        for line in order.lines:
            session.reserve(line.sku, line.qty)
        if order.gift_sku:
            attach_gift(book, session, order.gift_sku)
        _accept_coupon(order.coupon)
        pay_id = gateway.charge(order.user_id, order.amount_cents)
    except PaymentDeclined:
        raise
    except Exception:
        session.rollback()
        raise
    session.commit()
    return Receipt(
        order_id=order.order_id,
        user_id=order.user_id,
        pay_id=pay_id,
        lines=tuple(order.lines),
        gift_sku=order.gift_sku,
        amount_cents=order.amount_cents,
    )


def _validate_lines(lines):
    for line in lines:
        if not isinstance(line, OrderLine):
            raise ValueError("订单行不合法")
        if not isinstance(line.sku, str) or line.sku == "":
            raise ValueError("SKU 不能为空")
        if isinstance(line.qty, bool) or not isinstance(line.qty, int) or line.qty <= 0:
            raise ValueError("数量必须是正整数")


def _accept_coupon(coupon):
    if coupon not in _ACCEPTED_COUPONS:
        raise CouponError(coupon)
