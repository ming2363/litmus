import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from litmus.cli_player import main as player_main
from litmus.crypto import seal_dir
from litmus.integrity import append_audit, get_git_head
from litmus.report import (
    build_report_data,
    build_report_filename_stem,
    sanitize_filename_part,
)
from litmus.state import load_active_state, save_state
from litmus.tasks import load_all_tasks
from litmus.usage import TokenBucket, UsageSummary


FIXTURES = Path(__file__).resolve().parent / "fixtures"
FIXTURES_USAGE = FIXTURES / "usage"


def _prep_repo(root: Path) -> Path:
    subprocess.run(["git", "init"], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@litmus.local"], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=str(root), check=True, capture_output=True)
    (root / ".gitignore").write_bytes(("runs/\nreports/\nanswers/*/\n__pycache__/\n*.pyc\n").encode("utf-8"))
    (root / "litmus.py").write_bytes(("# entry\n").encode("utf-8"))
    (root / "litmus").mkdir()
    (root / "litmus" / "__init__.py").write_text("", encoding="utf-8")
    shutil.copytree(FIXTURES / "tasks", root / "tasks")
    (root / "answers").mkdir()
    for d in sorted((FIXTURES / "answers").iterdir()):
        if d.is_dir():
            seal_dir(d / "grade", root / "answers" / "{}.grade.enc".format(d.name))
            seal_dir(d / "solution", root / "answers" / "{}.solution.enc".format(d.name))
    subprocess.run(["git", "add", "."], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(root), check=True, capture_output=True)
    mode_file = root / "ai_relay_mode"
    mode_file.write_text("off\n", encoding="utf-8")
    return mode_file


class TestReport(unittest.TestCase):
    def test_sanitize_and_filename_stem(self):
        self.assertEqual(sanitize_filename_part("openai/gpt:5.1 test"), "openai-gpt-5.1-test")
        summary = UsageSummary(
            collected=True,
            tool="codex",
            models={"provider/gpt:6": TokenBucket(input_tokens=10)},
        )
        stem = build_report_filename_stem({"created_at": "2026-11-08T10:20:30+08:00"}, summary)
        self.assertEqual(stem, "20261108-102030-codex-provider-gpt-6")

        unknown_summary = UsageSummary(collected=False, tool="unknown", note="未采集")
        self.assertEqual(
            build_report_filename_stem({"created_at": "2026-11-08T10:20:30+08:00"}, unknown_summary),
            "20261108-102030-unknown-unknown",
        )

    def test_report_incomplete_tasks_validity_and_cli_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mode_file = _prep_repo(root)

            # 跑 quick 模式（2 题：bug-py-01, review-py-01），只做完第 1 题就出报告
            player_main(["start", "--quick"], root=root, ai_relay_mode_file=mode_file)
            player_main(["next"], root=root, ai_relay_mode_file=mode_file)
            run_dir, state = load_active_state(root)
            work1 = run_dir / "work" / "bug-py-01"
            shutil.copy2(FIXTURES / "answers" / "bug-py-01" / "solution" / "src" / "calc.py", work1 / "src" / "calc.py")
            # 模拟超时参考时长与重开 start 中断
            state["current_started_at"] = "2020-01-01T00:00:00+08:00"
            save_state(run_dir, state)
            player_main(["start"], root=root, ai_relay_mode_file=mode_file)
            player_main(["submit"], root=root, ai_relay_mode_file=mode_file)

            out_buf = io.StringIO()
            with contextlib.redirect_stdout(out_buf):
                rc = player_main(
                    ["report"],
                    root=root,
                    ai_relay_mode_file=mode_file,
                    usage_kwargs={
                        "claude_dir": Path("/nonexistent"),
                        "codex_dir": FIXTURES_USAGE / "codex",
                        "opencode_db": Path("/nonexistent/opencode.db"),
                    },
                )
            self.assertEqual(rc, 0)
            cli_out = out_buf.getvalue()
            self.assertTrue(cli_out.splitlines()[0].startswith("综合分："))
            self.assertIn("用浏览器打开查看完整报告", cli_out)
            self.assertNotIn("|---", cli_out)
            self.assertNotIn("author.py", cli_out)

            reports = list((root / "reports").glob("*.json"))
            self.assertEqual(len(reports), 1)
            data = json.loads(reports[0].read_text(encoding="utf-8"))
            self.assertTrue(data["validity"]["valid"])
            self.assertIn("score", data)
            self.assertIn("bank_version", data)
            self.assertEqual(len(data["bank_version"]), 12)
            self.assertEqual(data["summary"]["total"], 2)
            self.assertEqual(data["summary"]["passed"], 1)
            self.assertEqual(data["summary"]["incomplete_count"], 1)
            self.assertEqual(data["interruptions"]["resume_count"], 1)
            self.assertTrue(data["tasks"][0]["over_ref"])
            self.assertEqual(data["tasks"][1]["status"], "incomplete")
            self.assertEqual(data["tasks"][0]["credit"], 1.0)
            self.assertEqual(data["tasks"][1]["credit"], 0.0)
            self.assertEqual(data["usage"]["note"], "未采集")

            html_path = reports[0].with_suffix(".html")
            self.assertTrue(html_path.is_file())
            self.assertIn(str(html_path), cli_out)
            html_text = html_path.read_text(encoding="utf-8")
            self.assertIn("综合分", html_text)
            self.assertIn("有效", html_text)

            md_path = reports[0].with_suffix(".md")
            self.assertTrue(md_path.is_file())
            md_text = md_path.read_text(encoding="utf-8")
            self.assertIn("## 综合分：", md_text)
            self.assertIn("题库版本：`{}`".format(data["bank_version"]), md_text)
            self.assertIn("| r | 时间得分 | 计费等价 token | token 得分 |", md_text)
            self.assertIn("有效", md_text)
            self.assertIn("超过参考时长", md_text)
            self.assertIn("未完成", md_text)

    def test_invalidated_by_audit_unseal_or_git_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mode_file = _prep_repo(root)
            player_main(["start", "--quick"], root=root, ai_relay_mode_file=mode_file)
            run_dir, state = load_active_state(root)
            _, tasks = load_all_tasks(root)

            # 1) 注入非 grade 解密审计记录
            append_audit("unseal", task_id="bug-py-01", run_dir=None, root=root)
            # 2) 修改已跟踪文件
            (root / "litmus.py").write_text("# modified\n", encoding="utf-8")

            report_data = build_report_data(
                run_dir,
                state,
                tasks,
                root=root,
                usage_summary=UsageSummary(collected=False, tool="unknown", note="未采集"),
            )
            self.assertFalse(report_data["validity"]["valid"])
            joined = "\n".join(report_data["validity"]["reasons"])
            self.assertIn("unseal", joined)
            self.assertIn("已跟踪文件", joined)
            self.assertIsNotNone(get_git_head(root))


if __name__ == "__main__":
    unittest.main()
