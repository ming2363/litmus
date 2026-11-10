"""单文件 HTML 报告的渲染测试。"""

import re
import unittest
from html.parser import HTMLParser

from litmus.report import render_terminal_summary
from litmus.report_html import render_html


def _base_data():
    """与 tests/test_scoring.py 里 Markdown 渲染用例同一份骨架。"""
    return {
        "report_id": "20261109-test-valid",
        "mode": "full",
        "run_dir": "/tmp/test",
        "marker": "LITMUS-RUN-test",
        "bank_version": "f77556ac5cc6",
        "litmus_commit": "abc1234",
        "started_at": "2026-11-09T10:00:00+08:00",
        "finished_at": "2026-11-09T10:10:00+08:00",
        "env": {
            "python_version": "3.11.0",
            "java_version": "17.0.1",
            "javac_version": "17.0.1",
        },
        "validity": {"valid": True, "reasons": []},
        "summary": {
            "passed": 2,
            "total": 3,
            "score": 0.666667,
            "ci_95": [0.2, 0.9],
            "merge_veto_count": 0,
            "incomplete_count": 1,
            "skipped_count": 0,
            "review_extra_items_total": 0,
            "total_elapsed_s": 150.0,
            "wall_time_s": 600.0,
        },
        "score": {
            "composite": 63.92,
            "correctness": 66.67,
            "time_score": 0.85,
            "token_score": 0.81,
            "efficiency": 0.96,
            "token_collected": True,
        },
        "by_dimension": [
            {"key": "bug", "passed": 1, "total": 2, "rate": 0.5, "ci_95": [0.094, 0.906]},
            {"key": "custom_dim", "passed": 0, "total": 1, "rate": 0.0, "ci_95": [0.0, 0.793]},
        ],
        "by_difficulty": [
            {"key": "easy", "passed": 1, "total": 1, "rate": 1.0, "ci_95": [0.207, 1.0]},
            {"key": "long", "passed": 0, "total": 1, "rate": 0.0, "ci_95": [0.0, 0.793]},
            {"key": "nightmare", "passed": 0, "total": 1, "rate": 0.0, "ci_95": [0.0, 0.793]},
        ],
        "interruptions": {"resume_count": 0, "resumes": []},
        "usage": {
            "collected": True,
            "tool": "codex",
            "note": "",
            "total": {
                "input_tokens": 100,
                "output_tokens": 50,
                "cache_read_tokens": 20,
                "cache_write_tokens": 10,
                "reasoning_tokens": 5,
            },
            "models": {
                "gpt-test": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_read_tokens": 20,
                    "cache_write_tokens": 10,
                    "reasoning_tokens": 5,
                }
            },
        },
        "tasks": [
            {
                "seq": 1,
                "id": "task-01",
                "dimension": "bug",
                "difficulty": "easy",
                "status": "pass",
                "merge_veto": False,
                "elapsed_s": 30.0,
                "ref_minutes": 1.0,
                "r": 0.5,
                "time_score": 1.0,
                "effective_tokens": 30000.0,
                "token_score": 1.0,
                "over_ref": False,
                "reasons": [],
                "passed": True,
                "credit": 1.0,
            }
        ],
    }


def _with_status_rows(data):
    """补上部分得分、否决、未完成，以及带 HTML 的失败原因。"""
    data["tasks"] = [
        data["tasks"][0],
        {
            "seq": 2,
            "id": "long-py-01",
            "dimension": "feature",
            "difficulty": "long",
            "status": "fail",
            "merge_veto": False,
            "elapsed_s": 5400.0,
            "ref_minutes": 60,
            "r": 1.5,
            "time_score": 0.8,
            "effective_tokens": 900000,
            "token_score": 0.7,
            "over_ref": True,
            "reasons": ["F2P 通过 39/52"],
            "passed": False,
            "credit": 0.75,
        },
        {
            "seq": 3,
            "id": "feat-py-02",
            "dimension": "feature",
            "difficulty": "hard",
            "status": "fail",
            "merge_veto": True,
            "elapsed_s": 400.0,
            "ref_minutes": 15,
            "r": None,
            "time_score": None,
            "effective_tokens": None,
            "token_score": None,
            "over_ref": False,
            "reasons": ["改动超出允许范围"],
            "passed": False,
            "credit": 0.0,
        },
        {
            "seq": 4,
            "id": "review-py-01",
            "dimension": "review",
            "difficulty": "medium",
            "status": "incomplete",
            "merge_veto": False,
            "elapsed_s": None,
            "ref_minutes": 10,
            "r": None,
            "time_score": None,
            "effective_tokens": None,
            "token_score": None,
            "over_ref": False,
            "reasons": ["未提交"],
            "passed": False,
            "credit": 0.0,
        },
        {
            "seq": 5,
            "id": "<b>term-01</b>",
            "dimension": "terminal",
            "difficulty": "easy",
            "status": "fail",
            "merge_veto": False,
            "elapsed_s": 12.0,
            "ref_minutes": 5,
            "r": 0.04,
            "time_score": 1.0,
            "effective_tokens": 1000,
            "token_score": 1.0,
            "over_ref": False,
            "reasons": ["命令输出包含 <script>alert(1)</script>"],
            "passed": False,
            "credit": 0.0,
        },
    ]
    return data


class _RefCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.script_count = 0

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.script_count += 1
        for key, value in attrs:
            if key in ("src", "href") and value:
                self.refs.append(value)


class TestReportHtml(unittest.TestCase):
    def test_composite_and_valid_badge(self):
        html = render_html(_base_data())
        self.assertIn(">63.92<", html)
        self.assertIn(">有效<", html)
        self.assertNotIn(">无效<", html)
        self.assertIn("综合分 = 正确性分 × 效率系数", html)
        self.assertIn("修 Bug", html)
        self.assertIn("易", html)
        self.assertIn("custom_dim", html)
        self.assertIn("nightmare", html)
        self.assertIn("长任务", html)
        self.assertIn("Python", html)
        self.assertIn("abc1234", html)

    def test_invalid_report_shows_reasons(self):
        data = _base_data()
        data["validity"] = {
            "valid": False,
            "reasons": ["检测到未加密答案文件", "git 工作区受污染"],
        }
        html = render_html(data)
        self.assertIn(">无效<", html)
        self.assertIn("检测到未加密答案文件；git 工作区受污染", html)
        self.assertNotIn(">有效<", html)

    def test_failure_reason_html_is_escaped(self):
        html = render_html(_with_status_rows(_base_data()))
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("<b>term-01</b>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("&lt;b&gt;term-01&lt;/b&gt;", html)
        self.assertIn("<details>", html)
        self.assertIsNone(re.search(r"<details\b[^>]*\bopen\b", html))
        parser = _RefCollector()
        parser.feed(html)
        self.assertEqual(parser.script_count, 1)

    def test_partial_credit_label(self):
        html = render_html(_with_status_rows(_base_data()))
        self.assertIn(">部分得分<", html)
        self.assertIn('data-status="partial"', html)
        self.assertIn(">75%<", html)
        self.assertIn(">否决<", html)
        self.assertIn(">未完成<", html)
        self.assertEqual(html.count('<tr class="task-row'), 5)

    def test_failure_reasons_in_full_width_row(self):
        """失败原因单独占一整行并跟在所属题目行后面；通过的题没有原因行。"""
        html = render_html(_with_status_rows(_base_data()))
        rows = re.findall(r'<tr class="(task-row[^"]*|reason-row)"', html)
        self.assertIn("reason-row", rows)
        for i, cls in enumerate(rows):
            if cls == "reason-row":
                # 原因行前面一定是带原因标记的题目行
                self.assertEqual(rows[i - 1], "task-row has-reason")
            elif cls == "task-row has-reason":
                self.assertEqual(rows[i + 1], "reason-row")
        self.assertIn('colspan="14"', html)
        self.assertEqual(rows.count("reason-row"), rows.count("task-row has-reason"))

    def test_token_not_collected(self):
        data = _base_data()
        data["score"] = {
            "composite": 80.0,
            "correctness": 80.0,
            "time_score": 1.0,
            "token_score": None,
            "efficiency": 1.0,
            "token_collected": False,
        }
        data["usage"] = {
            "collected": False,
            "tool": "unknown",
            "note": "日志里没有这次运行标记",
            "total": {},
            "models": {},
        }
        html = render_html(data)
        self.assertIn(">未采集<", html)
        self.assertIn("效率系数只用时间分", html)
        self.assertIn("日志里没有这次运行标记", html)
        self.assertNotIn("<th>模型 ID</th>", html)

    def test_none_scores_show_wu(self):
        data = _base_data()
        data["score"] = {
            "composite": 0.0,
            "correctness": 0.0,
            "time_score": None,
            "token_score": None,
            "efficiency": None,
            "token_collected": True,
        }
        html = render_html(data)
        self.assertIn(">无<", html)

    def test_no_external_resources(self):
        pages = [
            render_html(_base_data()),
            render_html(_with_status_rows(_base_data())),
        ]
        data = _base_data()
        data["interruptions"] = {
            "resume_count": 1,
            "resumes": [{"at": "2026-11-09T10:05:00+08:00", "at_task": "task-01"}],
        }
        pages.append(render_html(data))
        for html in pages:
            self.assertNotIn("http://", html)
            self.assertNotIn("https://", html)
            parser = _RefCollector()
            parser.feed(html)
            for ref in parser.refs:
                self.assertFalse(ref.startswith("http://"))
                self.assertFalse(ref.startswith("https://"))
        self.assertIn("重新执行 start", pages[-1])

    def test_terminal_summary_lines(self):
        text = render_terminal_summary(_base_data())
        lines = text.strip().splitlines()
        self.assertEqual(lines[0], "综合分：63.92")
        self.assertEqual(
            lines[1],
            "正确性分：66.67 | 时间分：0.85 | token 分：0.81 | 效率系数：0.96",
        )
        self.assertEqual(lines[2], "通过 2/3 题，可合入性否决 0，未完成 1，跳过 0")
        self.assertNotIn("|---", text)

        invalid = _base_data()
        invalid["validity"] = {
            "valid": False,
            "reasons": ["检测到未加密答案文件", "git 工作区受污染"],
        }
        self.assertEqual(
            render_terminal_summary(invalid).splitlines()[0],
            "综合分：63.92（无效：检测到未加密答案文件；git 工作区受污染）",
        )

        missing = _base_data()
        missing["score"] = {
            "composite": 80.0,
            "correctness": 80.0,
            "time_score": 1.0,
            "token_score": None,
            "efficiency": 1.0,
            "token_collected": False,
        }
        self.assertIn("token 分：未采集（效率系数只用时间分）", render_terminal_summary(missing))


if __name__ == "__main__":
    unittest.main()
