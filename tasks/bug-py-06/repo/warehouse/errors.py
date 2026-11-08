"""结算过程中对外抛出的业务异常。"""


class WarehouseError(Exception):
    """库存和结算异常的共同基类。"""


class UnknownSku(WarehouseError):
    """账本里没有这个 SKU。"""

    def __init__(self, sku):
        super().__init__("未知 SKU: {}".format(sku))
        self.sku = sku


class InsufficientStock(WarehouseError):
    """可售数量不够完成本次预占。"""

    def __init__(self, sku):
        super().__init__("库存不足: {}".format(sku))
        self.sku = sku


class CouponError(WarehouseError):
    """优惠券不在允许的名单里。"""

    def __init__(self, code):
        super().__init__("优惠券无效: {}".format(code))
        self.code = code


class PaymentDeclined(WarehouseError):
    """支付网关拒绝了这笔收费。"""

    def __init__(self, reason):
        super().__init__("支付被拒: {}".format(reason))
        self.reason = reason
