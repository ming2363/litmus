"""随单赠品。赠品占用一件库存，并应跟商品一起提交或释放。"""

from warehouse.holds import HoldSession
from warehouse.stock import StockBook


def attach_gift(book: StockBook, session: HoldSession, gift_sku):
    """没有赠品时直接返回。有赠品时占一件。"""
    if gift_sku is None or gift_sku == "":
        return
    book.reserve(gift_sku, 1)
