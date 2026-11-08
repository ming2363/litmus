import unittest
from src.calc import add


class TestPublic(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
