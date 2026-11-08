import unittest

from src.pricing import compute_tariff


class TestPublic(unittest.TestCase):
    def test_basic_tariff_calculation(self):
        res = compute_tariff("cn", "us", 1200, "express", {"express": 0.9})
        self.assertEqual(res["origin"], "CN")
        self.assertEqual(res["dest"], "US")
        self.assertEqual(res["base_cents"], 2610)
        self.assertEqual(res["surcharge_cents"], 640)
        self.assertEqual(res["total_cents"], 2925)
        self.assertIn("override:applied", res["tags"])

    def test_custom_provider_and_validation(self):
        calls = [0]

        def provider(_o, _d, _t):
            calls[0] += 1
            return 1000 + calls[0] * 100

        r1 = compute_tariff("CN", "JP", 500, rate_provider=provider)
        r2 = compute_tariff("CN", "JP", 500, rate_provider=provider)
        self.assertNotEqual(r1["base_cents"], r2["base_cents"])
        with self.assertRaises(ValueError):
            compute_tariff("CN", "JP", 0)


if __name__ == "__main__":
    unittest.main()
