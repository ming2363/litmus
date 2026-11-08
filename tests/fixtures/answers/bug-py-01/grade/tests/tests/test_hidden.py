import unittest
from src.calc import safe_div


class TestHidden(unittest.TestCase):
    def test_div_normal(self):
        self.assertAlmostEqual(safe_div(6, 2), 3.0)

    def test_div_zero(self):
        with self.assertRaises(ValueError):
            safe_div(1, 0)
