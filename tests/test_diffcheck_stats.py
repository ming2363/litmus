import tempfile
import unittest
from pathlib import Path

from litmus.diffcheck import (
    DiffError,
    check_allowed_paths,
    compare_dirs,
    count_file_changed_lines,
    glob_match,
    is_visible_test_file,
)
from litmus.stats import wilson_interval


class TestDiffcheckAndStats(unittest.TestCase):
    def test_compare_dirs_ignores_build_artifacts_and_counts_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            work = root / "work"
            (repo / "src").mkdir(parents=True)
            (work / "src" / "__pycache__").mkdir(parents=True)
            (work / "out").mkdir(parents=True)

            (repo / "src" / "a.py").write_text("line1\nline2\nline3\n", encoding="utf-8", newline="\n")
            (repo / "src" / "old.py").write_text("x = 1\ny = 2\n", encoding="utf-8", newline="\n")

            # CRLF 和行尾空白归一化后，纯空白变更计为 0 行；仅 line2 实际改动
            (work / "src" / "a.py").write_bytes(b"line1  \r\nline2_fixed\r\nline3\r\n")
            (work / "src" / "new.py").write_text("z = 3\n", encoding="utf-8", newline="\n")
            # 构建产物应被忽略
            (work / "src" / "__pycache__" / "a.cpython-311.pyc").write_bytes(b"\x00\x01")
            (work / "out" / "Main.class").write_bytes(b"\xca\xfe\xba\xbe")
            (work / ".DS_Store").write_bytes(b"junk")

            summary = compare_dirs(repo, work)
            self.assertEqual(summary.added, ["src/new.py"])
            self.assertEqual(summary.modified, ["src/a.py"])
            self.assertEqual(summary.deleted, ["src/old.py"])
            self.assertEqual(summary.changed_files, ["src/a.py", "src/new.py", "src/old.py"])
            # a.py 改 1 行 + new.py 新增 1 行 + old.py 删除 2 行 = 4 行
            self.assertEqual(summary.changed_lines, 4)

    def test_pure_whitespace_diff_counts_zero_lines(self):
        self.assertEqual(count_file_changed_lines(b"a\nb\n", b"a  \r\nb\t\r\n"), 0)

    def test_symlink_in_workdir_raises_diff_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            work = root / "work"
            repo.mkdir()
            work.mkdir()
            (work / "evil").symlink_to("/etc/passwd")
            with self.assertRaises(DiffError):
                compare_dirs(repo, work)

    def test_glob_match_allowed_paths_and_visible_test_detection(self):
        self.assertTrue(glob_match("src/app.py", "src/*.py"))
        self.assertFalse(glob_match("src/sub/app.py", "src/*.py"))
        self.assertTrue(glob_match("src/sub/app.py", "src/**/*.py"))
        self.assertEqual(
            check_allowed_paths(["src/app.py", "tests/test_app.py"], ["src/*.py"]),
            ["tests/test_app.py"],
        )
        self.assertTrue(is_visible_test_file("tests/test_app.py"))
        self.assertTrue(is_visible_test_file("src/test/CalcTest.java"))
        self.assertFalse(is_visible_test_file("src/calc.py"))

    def test_wilson_interval(self):
        self.assertEqual(wilson_interval(0, 0), (0.0, 0.0))
        low, high = wilson_interval(8, 10)
        self.assertAlmostEqual(low, 0.49016, places=4)
        self.assertAlmostEqual(high, 0.94332, places=4)
        with self.assertRaises(ValueError):
            wilson_interval(5, 3)


if __name__ == "__main__":
    unittest.main()
