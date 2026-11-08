import io
from pathlib import Path
import tempfile
import unittest

from src.cli import main
from src.ledger import filter_entries, summarize_entries
from src.models import parse_iso_date
from src.storage import load_entries

SAMPLE_CSV = """id,date,category,kind,amount_cents,note
E1,2026-03-01,salary,income,500000,工资
E2,2026-03-05,food,expense,3500,午饭
E3,2026-03-10,food,expense,6500,晚饭
E4,2026-03-12,rent,expense,200000,房租
"""


class TestPublic(unittest.TestCase):
    def _write_csv(self, content: str) -> Path:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        p = Path(td.name) / "ledger.csv"
        p.write_text(content, encoding="utf-8", newline="\n")
        return p

    def test_parse_iso_date_valid(self):
        d = parse_iso_date("2026-03-10")
        self.assertEqual((d.year, d.month, d.day), (2026, 3, 10))

    def test_list_and_summary_without_since(self):
        csv_path = self._write_csv(SAMPLE_CSV)
        entries = load_entries(csv_path)
        self.assertEqual(len(entries), 4)

        food_only = filter_entries(entries, category="food")
        self.assertEqual([e.entry_id for e in food_only], ["E2", "E3"])

        summary = summarize_entries(food_only)
        self.assertEqual(summary["expense_cents"], 10000)

        out = io.StringIO()
        err = io.StringIO()
        rc = main(["summary", "--file", str(csv_path), "--category", "food"], stdout=out, stderr=err)
        self.assertEqual(rc, 0, err.getvalue())
        self.assertIn("总支出: 100.00", out.getvalue())
        self.assertIn("净结余: -100.00", out.getvalue())


if __name__ == "__main__":
    unittest.main()
