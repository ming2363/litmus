"""SKU 的可售、预占和已售数量。"""

from typing import Dict, Tuple

from warehouse.errors import InsufficientStock, UnknownSku


class StockBook:
    """内存账本。调用方负责在失败路径上把预占还回来。"""

    def __init__(self):
        self._rows: Dict[str, Tuple[int, int, int]] = {}

    def add_sku(self, sku, available):
        self._require_sku(sku)
        qty = self._require_non_negative(available, "可售数量")
        if sku in self._rows:
            raise ValueError("SKU 已存在")
        self._rows[sku] = (qty, 0, 0)

    def snapshot(self, sku):
        return self._row(sku)

    def reserve(self, sku, qty):
        amount = self._require_positive(qty, "预占数量")
        available, held, sold = self._row(sku)
        if available < amount:
            raise InsufficientStock(sku)
        self._rows[sku] = (available - amount, held + amount, sold)

    def release(self, sku, qty):
        amount = self._require_positive(qty, "释放数量")
        available, held, sold = self._row(sku)
        if held < amount:
            raise ValueError("预占数量不足")
        self._rows[sku] = (available + amount, held - amount, sold)

    def commit(self, sku, qty):
        amount = self._require_positive(qty, "成交数量")
        available, held, sold = self._row(sku)
        if held < amount:
            raise ValueError("预占数量不足")
        self._rows[sku] = (available, held - amount, sold + amount)

    def _row(self, sku):
        try:
            return self._rows[sku]
        except KeyError:
            raise UnknownSku(sku) from None

    @staticmethod
    def _require_sku(sku):
        if not isinstance(sku, str) or sku == "":
            raise ValueError("SKU 不能为空")

    @staticmethod
    def _require_non_negative(value, label):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("{}必须是非负整数".format(label))
        return value

    @staticmethod
    def _require_positive(value, label):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("{}必须是正整数".format(label))
        return value
