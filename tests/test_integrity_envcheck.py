import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from litmus.crypto import seal_dir
from litmus.envcheck import (
    check_ai_relay,
    check_and_clean_stale_grade_dirs,
    check_answers_sealed,
    check_crypto_verify,
    check_git_clean,
    check_no_forbidden_files,
    check_toolchains,
    run_env_checks,
)
from litmus.integrity import (
    append_audit,
    check_audit_during_run,
    check_run_integrity,
    get_git_head,
)
from litmus.state import now_iso


def _init_git_repo(root: Path) -> str:
    subprocess.run(["git", "init"], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@litmus.local"], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Litmus Test"], cwd=str(root), check=True, capture_output=True)
    (root / ".gitignore").write_text("runs/\nreports/\nanswers/*/\n", encoding="utf-8", newline="\n")
    (root / "litmus.py").write_text("# entry\n", encoding="utf-8", newline="\n")
    (root / "litmus").mkdir(exist_ok=True)
    (root / "litmus" / "__init__.py").write_text("", encoding="utf-8")
    (root / "tasks" / "t1" / "repo").mkdir(parents=True, exist_ok=True)
    (root / "tasks" / "t1" / "prompt.md").write_text("hi\n", encoding="utf-8")
    (root / "tasks" / "t1" / "task.json").write_text(
        json.dumps({
            "id": "t1", "dimension": "terminal", "lang": "none",
            "difficulty": "easy", "title": "t1", "ref_minutes": 1, "grader": "terminal",
        }),
        encoding="utf-8",
    )
    (root / "tasks" / "manifest.json").write_text(
        json.dumps({"version": 1, "order": ["t1"], "quick": ["t1"]}),
        encoding="utf-8",
    )
    plain = root / "plain_src"
    plain.mkdir()
    (plain / "check.py").write_text("import sys; sys.exit(0)\n", encoding="utf-8")
    (root / "answers").mkdir(exist_ok=True)
    seal_dir(plain, root / "answers" / "t1.grade.enc")
    shutil.rmtree(str(plain))
    subprocess.run(["git", "add", "."], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(root), check=True, capture_output=True)
    return get_git_head(root) or ""


class TestIntegrityAndEnvcheck(unittest.TestCase):
    def test_toolchains_checks_versions_and_missing_javac(self):
        item, info = check_toolchains()
        self.assertTrue(item.passed, item.detail)
        self.assertIn("python_version", info)

        # 只有 JRE 没有 javac 时应不满足
        bad_item, _ = check_toolchains(which_fn=lambda name: None if name == "javac" else "/usr/bin/" + name)
        self.assertFalse(bad_item.passed)
        self.assertIn("javac", bad_item.detail)

        # Java 11 < 17 应不满足
        def fake_run(cmd):
            if cmd[0] == "java":
                return 0, "", 'openjdk version "11.0.20" 2023-07-18'
            if cmd[0] == "javac":
                return 0, "javac 11.0.20", ""
            return 0, "git version 2.40.0", ""

        low_java, _ = check_toolchains(which_fn=lambda n: "/usr/bin/" + n, run_cmd_fn=fake_run)
        self.assertFalse(low_java.passed)
        self.assertIn("17", low_java.detail)

    def test_seven_checks_in_temp_git_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            head = _init_git_repo(root)
            mode_file = root / "ai_relay_mode"
            mode_file.write_text("off\n", encoding="utf-8")

            # 残留判分目录应被清理
            stale = root / "runs" / "20261108-000000-abcd" / ".grade" / "t1"
            stale.mkdir(parents=True)
            (stale / "leftover.txt").write_text("x", encoding="utf-8")

            res = run_env_checks(root, ai_relay_mode_file=mode_file)
            self.assertTrue(res.ok, [(i.name, i.passed, i.detail) for i in res.items])
            self.assertFalse((root / "runs" / "20261108-000000-abcd" / ".grade").exists())

            # ai-relay 非 off 失败
            mode_file.write_text("auto\n", encoding="utf-8")
            self.assertFalse(check_ai_relay(mode_file).passed)
            self.assertTrue(check_ai_relay(root / "nonexistent_mode").passed)

            # 出现明文目录失败
            (root / "answers" / "t1" / "grade").mkdir(parents=True)
            self.assertFalse(check_answers_sealed(root).passed)
            (root / "answers" / "t1" / "grade").rmdir()
            (root / "answers" / "t1").rmdir()

            # 出现禁止文件失败
            (root / "CLAUDE.md").write_text("# forbidden\n", encoding="utf-8")
            self.assertFalse(check_no_forbidden_files(root).passed)
            (root / "CLAUDE.md").unlink()

            # 篡改 litmus.py 后 git clean 与 integrity 均检出
            (root / "litmus.py").write_text("# tampered\n", encoding="utf-8")
            self.assertFalse(check_git_clean(root).passed)
            self.assertTrue(len(check_run_integrity(head, root)) > 0)

    def test_audit_log_detects_non_grade_decrypt_during_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            head = _init_git_repo(root)
            started = now_iso()
            append_audit("grade", task_id="t1", run_dir="run1", root=root)
            self.assertEqual(check_audit_during_run(started, "run1", root), [])

            append_audit("unseal", task_id="t1", run_dir=None, root=root)
            violations = check_audit_during_run(started, "run1", root)
            self.assertEqual(len(violations), 1)
            self.assertIn("unseal", violations[0])
            self.assertEqual(check_run_integrity(head, root), [])


if __name__ == "__main__":
    unittest.main()
