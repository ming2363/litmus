import json
import shutil
import tempfile
import unittest
from pathlib import Path

from litmus.graders import grade
from litmus.tasks import load_task


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestGradersOther(unittest.TestCase):
    def _prep(self, tmp: Path, task_id: str):
        shutil.copytree(FIXTURES / "tasks" / task_id, tmp / "tasks" / task_id)
        bundle = tmp / "bundle"
        shutil.copytree(FIXTURES / "answers" / task_id / "grade", bundle)
        task = load_task(task_id, root=tmp)
        work = tmp / "work"
        shutil.copytree(task.repo_dir, work)
        grade_dir = tmp / "grade_scratch"
        return task, work, grade_dir, bundle

    def test_terminal_grader(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            task, work, grade_dir, bundle = self._prep(tmp, "term-py-01")
            self.assertFalse(grade(task, work, grade_dir, bundle).passed)

            shutil.copy2(FIXTURES / "answers" / "term-py-01" / "solution" / "output.txt", work / "output.txt")
            res = grade(task, work, grade_dir, bundle)
            self.assertTrue(res.passed, res.reasons)

    def test_tool_call_grader_normalize_extra_args_ordered_and_empty(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            task, work, grade_dir, bundle = self._prep(tmp, "tool-none-01")

            # 非法 JSON 判不通过
            (work / "answer.json").write_text("{bad json", encoding="utf-8")
            self.assertFalse(grade(task, work, grade_dir, bundle).passed)

            # 日期格式与大小写归一化通过
            (work / "answer.json").write_text(
                json.dumps([{"name": "query_events", "args": {"date": "2026/11/8", "team": " CORE "}}]),
                encoding="utf-8",
            )
            self.assertTrue(grade(task, work, grade_dir, bundle).passed)

            # 多余参数判错
            (work / "answer.json").write_text(
                json.dumps([{"name": "query_events", "args": {"date": "2026-11-08", "team": "core", "extra": 1}}]),
                encoding="utf-8",
            )
            self.assertFalse(grade(task, work, grade_dir, bundle).passed)

            # 空列表预期（不调用）vs 非空提交
            (bundle / "expected.json").write_text(
                json.dumps({"ordered": True, "calls": [], "normalize": {}}),
                encoding="utf-8",
            )
            (work / "answer.json").write_text("[]", encoding="utf-8")
            self.assertTrue(grade(task, work, grade_dir, bundle).passed)
            (work / "answer.json").write_text(
                json.dumps([{"name": "delete_all", "args": {}}]),
                encoding="utf-8",
            )
            self.assertFalse(grade(task, work, grade_dir, bundle).passed)

            # 无序匹配（ordered=False）
            (bundle / "expected.json").write_text(
                json.dumps({
                    "ordered": False,
                    "calls": [{"name": "a", "args": {"x": 1}}, {"name": "b", "args": {"x": 2}}],
                    "normalize": {},
                }),
                encoding="utf-8",
            )
            (work / "answer.json").write_text(
                json.dumps([{"name": "b", "args": {"x": 2}}, {"name": "a", "args": {"x": 1}}]),
                encoding="utf-8",
            )
            self.assertTrue(grade(task, work, grade_dir, bundle).passed)
            # bool 与 int 严格区分：True != 1
            (work / "answer.json").write_text(
                json.dumps([{"name": "b", "args": {"x": 2}}, {"name": "a", "args": {"x": True}}]),
                encoding="utf-8",
            )
            self.assertFalse(grade(task, work, grade_dir, bundle).passed)

    def test_read_code_grader(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            task, work, grade_dir, bundle = self._prep(tmp, "read-py-01")
            (work / "answer.json").write_text(
                json.dumps([" Dispatcher#dispatch ", "Dispatcher#_route", "Dispatcher#_handle"]),
                encoding="utf-8",
            )
            self.assertTrue(grade(task, work, grade_dir, bundle).passed)

            # 顺序不对判不通过
            (work / "answer.json").write_text(
                json.dumps(["Dispatcher#_route", "Dispatcher#dispatch", "Dispatcher#_handle"]),
                encoding="utf-8",
            )
            self.assertFalse(grade(task, work, grade_dir, bundle).passed)

    def test_review_grader_optimal_pairing_max_items_and_extra(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            task, work, grade_dir, bundle = self._prep(tmp, "review-py-01")
            # 两个相近预埋问题验证精确最优配对（非贪心）
            (bundle / "expected.json").write_text(
                json.dumps({
                    "issues": [
                        {"file": "service.py", "line": 10, "category": "越界"},
                        {"file": "service.py", "line": 13, "category": "越界"},
                    ],
                    "categories": ["越界", "空指针"],
                    "max_items": 10,
                    "line_tolerance": 3,
                }),
                encoding="utf-8",
            )
            # 12 距离 13 仅 1 行，但如果贪心抢走 13，15 就配不上 10；最优配对 (12->10, 15->13) 应全中
            (work / "review.json").write_text(
                json.dumps([
                    {"file": "./service.py", "line": 12, "category": "越界", "description": "a"},
                    {"file": "service.py", "line": 15, "category": "越界", "description": "b"},
                    {"file": "service.py", "line": 20, "category": "空指针", "description": "额外条目"},
                ]),
                encoding="utf-8",
            )
            res = grade(task, work, grade_dir, bundle)
            self.assertTrue(res.passed, res.reasons)
            self.assertEqual(res.extra["extra_items"], 1)

            # 超过 max_items 判不通过
            too_many = [
                {"file": "service.py", "line": i + 1, "category": "越界", "description": "spam"}
                for i in range(11)
            ]
            (work / "review.json").write_text(json.dumps(too_many), encoding="utf-8")
            self.assertFalse(grade(task, work, grade_dir, bundle).passed)


if __name__ == "__main__":
    unittest.main()
