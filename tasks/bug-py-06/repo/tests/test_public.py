import unittest

from warehouse.checkout import checkout
from warehouse.errors import InsufficientStock, UnknownSku
from warehouse.holds import HoldSession
from warehouse.models import Order, OrderLine
from warehouse.stock import StockBook


class _Gateway:
    def __init__(self, pay_id="pay-1"):
        self.pay_id = pay_id
        self.calls = []

    def charge(self, user_id, amount_cents):
        self.calls.append((user_id, amount_cents))
        return self.pay_id


class TestPublic(unittest.TestCase):
    def test_reserve_release_and_commit(self):
        book = StockBook()
        book.add_sku("mug", 5)
        book.reserve("mug", 2)
        self.assertEqual(book.snapshot("mug"), (3, 2, 0))
        book.release("mug", 1)
        self.assertEqual(book.snapshot("mug"), (4, 1, 0))
        book.commit("mug", 1)
        self.assertEqual(book.snapshot("mug"), (4, 0, 1))

    def test_reject_bad_stock_arguments(self):
        book = StockBook()
        with self.assertRaises(ValueError):
            book.add_sku("", 1)
        with self.assertRaises(ValueError):
            book.add_sku("mug", True)
        with self.assertRaises(ValueError):
            book.add_sku("mug", -1)
        book.add_sku("mug", 1)
        with self.assertRaises(ValueError):
            book.add_sku("mug", 1)
        with self.assertRaises(InsufficientStock) as shortage:
            book.reserve("mug", 2)
        self.assertEqual(shortage.exception.sku, "mug")
        self.assertEqual(book.snapshot("mug"), (1, 0, 0))
        with self.assertRaises(UnknownSku) as missing:
            book.snapshot("gone")
        self.assertEqual(missing.exception.sku, "gone")
        with self.assertRaises(ValueError):
            book.release("mug", 1)

    def test_checkout_two_lines(self):
        book = StockBook()
        book.add_sku("mug", 4)
        book.add_sku("cup", 3)
        gateway = _Gateway("pay-9")
        order = Order(
            "o-1",
            "u-1",
            (OrderLine("mug", 2), OrderLine("cup", 1)),
            None,
            None,
            1800,
        )
        receipt = checkout(book, gateway, order)
        self.assertEqual(receipt.pay_id, "pay-9")
        self.assertEqual(receipt.order_id, "o-1")
        self.assertEqual(receipt.user_id, "u-1")
        self.assertEqual(receipt.amount_cents, 1800)
        self.assertIsNone(receipt.gift_sku)
        self.assertEqual([(line.sku, line.qty) for line in receipt.lines], [("mug", 2), ("cup", 1)])
        self.assertEqual(book.snapshot("mug"), (2, 0, 2))
        self.assertEqual(book.snapshot("cup"), (2, 0, 1))
        self.assertEqual(gateway.calls, [("u-1", 1800)])
        self.assertEqual(order.lines[0].qty, 2)

    def test_coupon_save10(self):
        book = StockBook()
        book.add_sku("mug", 2)
        gateway = _Gateway()
        order = Order("o-2", "u-2", (OrderLine("mug", 1),), "", "SAVE10", 900)
        receipt = checkout(book, gateway, order)
        self.assertEqual(receipt.gift_sku, "")
        self.assertEqual(book.snapshot("mug"), (1, 0, 1))
        self.assertEqual(gateway.calls, [("u-2", 900)])

    def test_invalid_line_does_not_charge(self):
        book = StockBook()
        book.add_sku("mug", 3)
        gateway = _Gateway()
        for line in (OrderLine("mug", True), OrderLine("mug", 0), OrderLine("", 1)):
            order = Order("o-3", "u-3", (line,), None, None, 100)
            with self.assertRaises(ValueError):
                checkout(book, gateway, order)
        self.assertEqual(book.snapshot("mug"), (3, 0, 0))
        self.assertEqual(gateway.calls, [])

    def test_single_hold_round_trip(self):
        book = StockBook()
        book.add_sku("mug", 4)
        session = HoldSession(book)
        session.reserve("mug", 2)
        session.rollback()
        self.assertEqual(book.snapshot("mug"), (4, 0, 0))
        session.rollback()
        self.assertEqual(book.snapshot("mug"), (4, 0, 0))
        session.reserve("mug", 3)
        session.commit()
        self.assertEqual(book.snapshot("mug"), (1, 0, 3))
        session.commit()
        self.assertEqual(book.snapshot("mug"), (1, 0, 3))
