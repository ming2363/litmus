import unittest

from src.identifiers import extract_parcel_codes, is_valid_parcel_code, parse_parcel_code
from src.manifest import summarize_dispatch_log


class TestPublic(unittest.TestCase):
    def test_legacy_parcel_code_still_valid(self):
        self.assertTrue(is_valid_parcel_code("SH-2026-00412"))
        parsed = parse_parcel_code("SH-2026-00412")
        self.assertEqual(
            parsed,
            {
                "site": "SH",
                "zone": None,
                "year": "2026",
                "seq": "00412",
                "suffix": None,
            },
        )

    def test_basic_extract_and_summary(self):
        log = "发货清单：SH-2026-00412 已出库，BJ-2025-10001 待复核。"
        self.assertEqual(extract_parcel_codes(log), ["SH-2026-00412", "BJ-2025-10001"])
        summary = summarize_dispatch_log(log)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["by_site"], {"BJ": 1, "SH": 1})


if __name__ == "__main__":
    unittest.main()
