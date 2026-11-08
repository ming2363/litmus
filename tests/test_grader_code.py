import shutil
import tempfile
import unittest
from pathlib import Path

from litmus.graders import grade
from litmus.tasks import load_task


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestGraderCode(unittest.TestCase):
    def _copy_fixture_task(self, tmp: Path, task_id: str):
        tasks_root = tmp / "tasks" / task_id
        shutil.copytree(FIXTURES / "tasks" / task_id, tasks_root)
        bundle = tmp / "bundle"
        shutil.copytree(FIXTURES / "answers" / task_id / "grade", bundle)
        task = load_task(task_id, root=tmp)
        work = tmp / "work"
        shutil.copytree(task.repo_dir, work)
        grade_dir = tmp / "grade_scratch"
        return task, work, grade_dir, bundle

    def test_python_code_grader_pass_veto_and_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            task, work, grade_dir, bundle = self._copy_fixture_task(tmp, "bug-py-01")

            # 1) 起始代码应不通过且不是 merge_veto
            res_init = grade(task, work, grade_dir, bundle)
            self.assertFalse(res_init.passed)
            self.assertFalse(res_init.merge_veto)
            self.assertFalse((grade_dir / "eval").exists())

            # 2) 应用参考解后应通过
            shutil.copy2(FIXTURES / "answers" / "bug-py-01" / "solution" / "src" / "calc.py", work / "src" / "calc.py")
            res_pass = grade(task, work, grade_dir, bundle)
            self.assertTrue(res_pass.passed, res_pass.reasons)
            self.assertFalse(res_pass.merge_veto)
            self.assertFalse((grade_dir / "eval").exists())

            # 3) 超出 max_changed_lines 应可合入性否决
            (work / "src" / "calc.py").write_text(
                "def add(a, b):\n    return a + b\n\ndef safe_div(a, b):\n    if b == 0:\n        raise ValueError('zero')\n    x1 = 1\n    x2 = 2\n    x3 = 3\n    x4 = 4\n    return a / b\n",
                encoding="utf-8",
            )
            res_lines = grade(task, work, grade_dir, bundle)
            self.assertFalse(res_lines.passed)
            self.assertTrue(res_lines.merge_veto)

            # 4) 修改可见测试应触发可合入性否决
            shutil.copy2(FIXTURES / "answers" / "bug-py-01" / "solution" / "src" / "calc.py", work / "src" / "calc.py")
            (work / "tests" / "test_public.py").write_text("# modified\n", encoding="utf-8")
            res_veto = grade(task, work, grade_dir, bundle)
            self.assertFalse(res_veto.passed)
            self.assertTrue(res_veto.merge_veto)

    def test_java_code_grader_pass_and_tampered_visible_test_veto(self):
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            task, work, grade_dir, bundle = self._copy_fixture_task(tmp, "bug-java-01")

            res_init = grade(task, work, grade_dir, bundle)
            self.assertFalse(res_init.passed)
            self.assertFalse(res_init.merge_veto)

            shutil.copy2(FIXTURES / "answers" / "bug-java-01" / "solution" / "Calc.java", work / "Calc.java")
            res_pass = grade(task, work, grade_dir, bundle)
            self.assertTrue(res_pass.passed, res_pass.reasons)

            # 允许路径外改动应触发可合入性否决
            (work / "Extra.java").write_text("public class Extra {}\n", encoding="utf-8")
            res_veto = grade(task, work, grade_dir, bundle)
            self.assertFalse(res_veto.passed)
            self.assertTrue(res_veto.merge_veto)


if __name__ == "__main__":
    unittest.main()
