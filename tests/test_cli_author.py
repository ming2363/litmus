import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from litmus.cli_author import main as author_main
from litmus.integrity import read_audit_log
from litmus.state import create_run, save_state


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _run_author(argv, root: Path):
    out = io.StringIO()
    err = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = author_main(argv, root=root)
    return rc, out.getvalue(), err.getvalue()


class TestCliAuthor(unittest.TestCase):
    def _prep_author_workspace(self, root: Path) -> None:
        shutil.copytree(FIXTURES / "tasks", root / "tasks")
        shutil.copytree(FIXTURES / "answers", root / "answers")

    def test_seal_unseal_selftest_and_lint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prep_author_workspace(root)

            # 1) lint 通过
            rc, out, _ = _run_author(["lint"], root)
            self.assertEqual(rc, 0, out)

            # 2) seal --all 加密并删除明文目录
            rc, out, _ = _run_author(["seal", "--all"], root)
            self.assertEqual(rc, 0, out)
            for tid in ("bug-py-01", "bug-java-01", "term-py-01", "tool-none-01", "read-py-01", "review-py-01"):
                self.assertTrue((root / "answers" / "{}.grade.enc".format(tid)).is_file())
                self.assertTrue((root / "answers" / "{}.solution.enc".format(tid)).is_file())
                self.assertFalse((root / "answers" / tid).exists())

            # 3) selftest 全部 6 题（起始失败 x3 + 参考解通过 x3）
            rc, out, _ = _run_author(["selftest"], root)
            self.assertEqual(rc, 0, out)

            # 4) unseal 解密回明文并写审计
            rc, out, _ = _run_author(["unseal", "bug-py-01"], root)
            self.assertEqual(rc, 0, out)
            self.assertTrue((root / "answers" / "bug-py-01" / "grade" / "meta.json").is_file())
            self.assertTrue((root / "answers" / "bug-py-01" / "solution" / "src" / "calc.py").is_file())

            entries, errs = read_audit_log(root)
            self.assertEqual(errs, [])
            ops = [e["op"] for e in entries]
            self.assertIn("seal", ops)
            self.assertIn("selftest", ops)
            self.assertIn("unseal", ops)

    def test_unseal_and_selftest_refuse_when_active_run_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prep_author_workspace(root)
            _run_author(["seal", "--all"], root)

            run_dir, state = create_run("quick", "deadbeef", ["bug-py-01"], root=root)
            rc_u, out_u, _ = _run_author(["unseal", "bug-py-01"], root)
            self.assertNotEqual(rc_u, 0)
            self.assertIn("未完成", out_u)

            rc_s, out_s, _ = _run_author(["selftest", "bug-py-01"], root)
            self.assertNotEqual(rc_s, 0)
            self.assertIn("未完成", out_s)

            # 测评完成后恢复可用
            state["status"] = "done"
            save_state(run_dir, state)
            rc_s2, out_s2, _ = _run_author(["selftest", "bug-py-01"], root)
            self.assertEqual(rc_s2, 0, out_s2)

    def test_lint_detects_forbidden_file_and_selftest_catches_broken_solution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prep_author_workspace(root)
            (root / "AGENTS.md").write_text("# forbidden", encoding="utf-8")
            rc_lint, out_lint, _ = _run_author(["lint"], root)
            self.assertNotEqual(rc_lint, 0)
            self.assertIn("AGENTS.md", out_lint)

            # 破坏参考解后 selftest 应失败
            (root / "answers" / "read-py-01" / "solution" / "answer.json").write_text(
                json.dumps(["wrong"]), encoding="utf-8"
            )
            _run_author(["seal", "read-py-01"], root)
            rc_st, out_st, _ = _run_author(["selftest", "read-py-01"], root)
            self.assertNotEqual(rc_st, 0)


if __name__ == "__main__":
    unittest.main()
