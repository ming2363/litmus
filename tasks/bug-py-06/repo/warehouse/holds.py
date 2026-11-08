"""一笔订单内的预占清单。"""

from warehouse.stock import StockBook


class HoldSession:
    """记下本次结算成功预占的每一行，供提交或释放。"""

    def __init__(self, book: StockBook):
        self.book = book
        self._holds = []

    def reserve(self, sku, qty):
        self.book.reserve(sku, qty)
        self._holds.append((sku, qty))

    def rollback(self):
        if not self._holds:
            return
        sku, qty = self._holds[-1]
        self.book.release(sku, qty)
        self._holds.clear()

    def commit(self):
        for sku, qty in self._holds:
            self.book.commit(sku, qty)
        self._holds.clear()
