import subprocess
import sys
import unittest
from pathlib import Path

from litmus import paths


class TestScaffold(unittest.TestCase):
    def test_paths_constants_and_ignored_rules(self):
        # 校验禁止文件名与忽略清单
        self.assertEqual(paths.FORBIDDEN_FILES, ("AGENTS.md", "CLAUDE.md", "GEMINI.md"))
        for expected in ("*.class", "out/", "build/", "target/", "__pycache__/", "*.pyc", ".pytest_cache/", ".git/", ".DS_Store"):
            self.assertIn(expected, paths.IGNORE_PATTERNS)

        self.assertTrue(paths.is_ignored_relpath("out/Main.class"))
        self.assertTrue(paths.is_ignored_relpath("src/__pycache__/calc.cpython-311.pyc"))
        self.assertTrue(paths.is_ignored_relpath(".DS_Store"))
        self.assertTrue(paths.is_ignored_relpath(".git/HEAD"))
        self.assertFalse(paths.is_ignored_relpath("src/main.py"))

    def test_prompt_and_gitignore_exist(self):
        root = paths.get_repo_root()
        prompt_text = (root / "PROMPT.md").read_text(encoding="utf-8")
        self.assertIn("python3 litmus.py start", prompt_text)
        self.assertIn("python3 litmus.py start --quick", prompt_text)
        self.assertIn("ALL DONE", prompt_text)

        gi_lines = (root / ".gitignore").read_text(encoding="utf-8").splitlines()
        for entry in ("runs/", "reports/", "answers/*/", "__pycache__/", "*.pyc"):
            self.assertIn(entry, gi_lines)

    def test_cli_entrypoints_help_and_isolation(self):
        root = paths.get_repo_root()
        res_player = subprocess.run(
            [sys.executable, str(root / "litmus.py"), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_player.returncode, 0)
        # 做题入口帮助文本禁止出现 author.py
        self.assertNotIn("author.py", res_player.stdout)
        self.assertNotIn("author.py", res_player.stderr)

        res_author = subprocess.run(
            [sys.executable, str(root / "author.py"), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res_author.returncode, 0)
        self.assertIn("author.py", res_author.stdout)


if __name__ == "__main__":
    unittest.main()
