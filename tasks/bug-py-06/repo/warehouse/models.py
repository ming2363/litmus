"""下单时在各模块之间传递的冻结数据。"""

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple


@dataclass(frozen=True)
class OrderLine:
    """一行商品。数量的合法性由结算入口检查。"""

    sku: str
    qty: int


@dataclass(frozen=True)
class Order:
    """一张待结算订单。金额由调用方算好，这里不重新计价。"""

    order_id: str
    user_id: str
    lines: Sequence[OrderLine]
    gift_sku: Optional[str]
    coupon: Optional[str]
    amount_cents: int


@dataclass(frozen=True)
class Receipt:
    """收费成功后交给上游的回执。"""

    order_id: str
    user_id: str
    pay_id: str
    lines: Tuple[OrderLine, ...]
    gift_sku: Optional[str]
    amount_cents: int
