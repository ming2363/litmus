import sqlite3
import tempfile
import unittest
from pathlib import Path

from litmus.usage import collect


FIXTURES_USAGE = Path(__file__).resolve().parent / "fixtures" / "usage"


class TestUsageCollectors(unittest.TestCase):
    def test_claude_collector_subagents_dedup_and_task_split(self):
        summary = collect(
            "LITMUS-RUN-a1b2c3",
            ["bug-py-01", "review-py-01"],
            root=Path("/tmp/demo"),
            claude_dir=FIXTURES_USAGE / "claude",
            codex_dir=Path("/nonexistent"),
            opencode_db=Path("/nonexistent/opencode.db"),
        )
        self.assertTrue(summary.collected)
        self.assertEqual(summary.tool, "claude")
        # bug-py-01 包含 msg_2 + agent-sub1；review-py-01 包含 msg_3；msg_1 在题目标记之前
        self.assertEqual(summary.by_task["bug-py-01"].input_tokens, 25)
        self.assertEqual(summary.by_task["bug-py-01"].output_tokens, 72)
        self.assertEqual(summary.by_task["bug-py-01"].reasoning_tokens, 28)
        self.assertEqual(summary.by_task["review-py-01"].input_tokens, 30)
        # req_1 去重后只算一次（output=40 而非 8+40）
        self.assertEqual(summary.total.output_tokens, 40 + 60 + 12 + 25)
        self.assertEqual(summary.total.cache_read_tokens, 100 + 200 + 10)
        self.assertEqual(summary.total.cache_write_tokens, 50 + 10)
        self.assertEqual(set(summary.models.keys()), {"claude-opus-5-5", "claude-sonnet-5"})

    def test_codex_collector_dedup_and_split(self):
        summary = collect(
            "LITMUS-RUN-c0de01",
            ["bug-py-01", "review-py-01"],
            claude_dir=Path("/nonexistent"),
            codex_dir=FIXTURES_USAGE / "codex",
            opencode_db=Path("/nonexistent/opencode.db"),
        )
        self.assertTrue(summary.collected)
        self.assertEqual(summary.tool, "codex")
        self.assertEqual(summary.total.input_tokens, 150)
        self.assertEqual(summary.total.output_tokens, 50)
        self.assertEqual(summary.total.cache_read_tokens, 50)
        self.assertEqual(summary.total.cache_write_tokens, 5)
        self.assertEqual(summary.total.reasoning_tokens, 12)
        self.assertEqual(summary.by_task["bug-py-01"].input_tokens, 100)
        self.assertEqual(summary.by_task["review-py-01"].input_tokens, 50)
        self.assertEqual(set(summary.models.keys()), {"gpt-6.1-sol"})

    def test_opencode_collector_readonly_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "opencode.db"
            conn = sqlite3.connect(str(db_path))
            conn.executescript((FIXTURES_USAGE / "opencode.sql").read_text(encoding="utf-8"))
            conn.commit()
            conn.close()

            summary = collect(
                "LITMUS-RUN-oc0001",
                ["bug-py-01", "review-py-01"],
                claude_dir=Path("/nonexistent"),
                codex_dir=Path("/nonexistent"),
                opencode_db=db_path,
            )
            self.assertTrue(summary.collected)
            self.assertEqual(summary.tool, "opencode")
            self.assertEqual(summary.by_task["bug-py-01"].input_tokens, 48)
            self.assertEqual(summary.by_task["review-py-01"].input_tokens, 60)
            self.assertEqual(summary.total.output_tokens, 5 + 15 + 4 + 25)
            self.assertEqual(set(summary.models.keys()), {"kimi-k3.1-pro", "qwen3.8-max"})

    def test_missing_marker_returns_uncollected(self):
        summary = collect(
            "LITMUS-RUN-ffffff",
            ["bug-py-01"],
            claude_dir=Path("/nonexistent"),
            codex_dir=Path("/nonexistent"),
            opencode_db=Path("/nonexistent/opencode.db"),
        )
        self.assertFalse(summary.collected)
        self.assertEqual(summary.tool, "unknown")
        self.assertEqual(summary.note, "未采集")


if __name__ == "__main__":
    unittest.main()


class TestSafeInt(unittest.TestCase):
    def test_bad_values_become_zero_instead_of_raising(self):
        from litmus.usage import safe_int

        self.assertEqual(safe_int(12), 12)
        self.assertEqual(safe_int("34"), 34)
        self.assertEqual(safe_int("5.0"), 5)
        self.assertEqual(safe_int(None), 0)
        self.assertEqual(safe_int("abc"), 0)
        self.assertEqual(safe_int({"x": 1}), 0)
        self.assertEqual(safe_int(True), 0)
