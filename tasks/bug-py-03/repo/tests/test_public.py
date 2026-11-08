import unittest

from accesslog.parser import parse_line, parse_lines
from accesslog.summary import by_level, slowest


class TestPublic(unittest.TestCase):
    def test_simple_line(self):
        row = parse_line(
            "2026-11-08T01:02:03Z INFO checkout.pay duration_ms=15 key=order.created message=paid ok"
        )
        self.assertEqual(row["date"], "2026-11-08T01:02:03Z")
        self.assertEqual(row["level"], "INFO")
        self.assertEqual(row["event"], "checkout.pay")
        self.assertEqual(row["duration_ms"], 15)
        self.assertEqual(row["key"], "order.created")
        self.assertEqual(row["message"], "paid ok")

    def test_empty_message_and_blank_lines(self):
        text = "\n2026-11-08T01:02:03Z WARN job.sync duration_ms=3 key=a.b message=\n\n"
        rows = parse_lines(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["message"], "")
        self.assertEqual(rows[0]["duration_ms"], 3)

    def test_reject_malformed(self):
        raw = "not a log line"
        with self.assertRaises(ValueError) as caught:
            parse_line(raw)
        self.assertIn(raw, str(caught.exception))

    def test_summary_and_slowest(self):
        text = "\n".join(
            [
                "2026-11-08T01:02:03Z INFO checkout.pay duration_ms=15 key=order.created message=paid ok",
                "2026-11-08T01:02:04Z INFO checkout.pay duration_ms=4 key=order.created message=paid ok",
                "2026-11-08T01:02:05Z ERROR checkout.pay duration_ms=40 key=order.created message=nope",
            ]
        )
        self.assertEqual(by_level(text), {"INFO": 2, "ERROR": 1})
        self.assertEqual(slowest(text)["duration_ms"], 40)
