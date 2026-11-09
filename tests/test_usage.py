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
        # 统一口径后 input_tokens 扣除 cached_input_tokens: (100-40) + (50-10) = 100
        self.assertEqual(summary.total.input_tokens, 100)
        self.assertEqual(summary.total.output_tokens, 50)
        self.assertEqual(summary.total.cache_read_tokens, 50)
        self.assertEqual(summary.total.cache_write_tokens, 5)
        self.assertEqual(summary.total.reasoning_tokens, 12)
        self.assertEqual(summary.by_task["bug-py-01"].input_tokens, 60)
        self.assertEqual(summary.by_task["review-py-01"].input_tokens, 40)
        self.assertEqual(set(summary.models.keys()), {"gpt-6.1-sol"})

    def test_codex_token_conversion_subtracts_cache(self):
        """单独验证 Codex 解析器口径转换：input_tokens = max(0, input - cached)。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            rollout = tmp_path / "rollout-demo.jsonl"
            lines = [
                '{"type":"turn_context","payload":{"model":"gpt-test"}}',
                '{"type":"response_item","payload":{"type":"text","output":"运行标记: LITMUS-RUN-test01\\nLITMUS-TASK-bug-01"}}',
                '{"type":"event_msg","payload":{"type":"token_count","info":{"total_token_usage":{"input_tokens":1000,"cached_input_tokens":700,"cache_write_input_tokens":50,"output_tokens":200,"reasoning_output_tokens":80}}}}',
            ]
            rollout.write_text("\n".join(lines) + "\n", encoding="utf-8")
            summary = collect(
                "LITMUS-RUN-test01",
                ["bug-01"],
                codex_dir=tmp_path,
                claude_dir=Path("/nonexistent"),
                opencode_db=Path("/nonexistent/opencode.db"),
            )
            self.assertTrue(summary.collected)
            bucket = summary.by_task["bug-01"]
            # 1000 - 700 = 300
            self.assertEqual(bucket.input_tokens, 300)
            self.assertEqual(bucket.cache_read_tokens, 700)
            self.assertEqual(bucket.output_tokens, 200)
            self.assertEqual(bucket.reasoning_tokens, 80)

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
            # 统一口径后 output_tokens 包含 reasoning_tokens: (5+1) + (15+3) + (4+0) + (25+6) = 59
            self.assertEqual(summary.total.output_tokens, (5 + 1) + (15 + 3) + (4 + 0) + (25 + 6))
            self.assertEqual(set(summary.models.keys()), {"kimi-k3.1-pro", "qwen3.8-max"})

    def test_opencode_token_conversion_includes_reasoning(self):
        """单独验证 OpenCode 解析器口径转换：output = output + reasoning。"""
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "opencode.db"
            conn = sqlite3.connect(str(db_path))
            conn.executescript("""
            CREATE TABLE session (id TEXT PRIMARY KEY, parent_id TEXT, directory TEXT, model TEXT, time_created INT, time_updated INT);
            CREATE TABLE message (id TEXT PRIMARY KEY, session_id TEXT, time_created INT, time_updated INT, data TEXT);
            CREATE TABLE part (id TEXT PRIMARY KEY, message_id TEXT, session_id TEXT, time_created INT, time_updated INT, data TEXT);
            INSERT INTO session VALUES ('s1', NULL, '/tmp', 'm1', 10, 20);
            INSERT INTO part VALUES ('p1', 'm0', 's1', 11, 11, '{"type":"text","text":"LITMUS-RUN-test02\\nLITMUS-TASK-feat-01"}');
            INSERT INTO message VALUES ('m1', 's1', 12, 12, '{"role":"assistant","modelID":"m1","tokens":{"input":100,"output":50,"reasoning":30,"cache":{"read":10,"write":5}}}');
            """)
            conn.commit()
            conn.close()

            summary = collect(
                "LITMUS-RUN-test02",
                ["feat-01"],
                opencode_db=db_path,
                claude_dir=Path("/nonexistent"),
                codex_dir=Path("/nonexistent"),
            )
            self.assertTrue(summary.collected)
            bucket = summary.by_task["feat-01"]
            # 50 + 30 = 80
            self.assertEqual(bucket.output_tokens, 80)
            self.assertEqual(bucket.reasoning_tokens, 30)
            self.assertEqual(bucket.input_tokens, 100)

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
