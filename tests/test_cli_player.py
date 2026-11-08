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
from litmus.state import load_active_state


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _build_temp_litmus_repo(root: Path) -> Path:
    subprocess.run(["git", "init"], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@litmus.local"], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=str(root), check=True, capture_output=True)

    (root / ".gitignore").write_text("runs/\nreports/\nanswers/*/\n__pycache__/\n*.pyc\n", encoding="utf-8", newline="\n")
    (root / "litmus.py").write_text("# player entry\n", encoding="utf-8", newline="\n")
    (root / "litmus").mkdir()
    (root / "litmus" / "__init__.py").write_text("", encoding="utf-8")
    shutil.copytree(FIXTURES / "tasks", root / "tasks")
    (root / "answers").mkdir()
    for task_dir in sorted((FIXTURES / "answers").iterdir()):
        if not task_dir.is_dir():
            continue
        seal_dir(task_dir / "grade", root / "answers" / "{}.grade.enc".format(task_dir.name))
        seal_dir(task_dir / "solution", root / "answers" / "{}.solution.enc".format(task_dir.name))

    subprocess.run(["git", "add", "."], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "fixture repo"], cwd=str(root), check=True, capture_output=True)
    mode_file = root / "ai_relay_mode"
    mode_file.write_text("off\n", encoding="utf-8")
    return mode_file


def _run_cli(argv, root: Path, mode_file: Path):
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        rc = player_main(argv, root=root, ai_relay_mode_file=mode_file)
    return rc, buf_out.getvalue(), buf_err.getvalue()


class TestCliPlayerE2E(unittest.TestCase):
    def test_end_to_end_full_flow_and_edge_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mode_file = _build_temp_litmus_repo(root)

            # 1) start 创建快速模式测评（2 题：bug-py-01, review-py-01）
            rc, out, _ = _run_cli(["start", "--quick"], root, mode_file)
            self.assertEqual(rc, 0, out)
            self.assertIn("LITMUS-RUN-", out)
            self.assertNotIn("author.py", out)
            self.assertTrue(out.strip().splitlines()[-1].startswith("下一步："))

            # 2) next 发第 1 题；未提交前重复调用 next 不跳题
            rc, out1, _ = _run_cli(["next"], root, mode_file)
            self.assertEqual(rc, 0, out1)
            self.assertIn("LITMUS-TASK-bug-py-01", out1)
            rc, out1_again, _ = _run_cli(["next"], root, mode_file)
            self.assertEqual(rc, 0)
            self.assertIn("LITMUS-TASK-bug-py-01", out1_again)

            _, state = load_active_state(root)
            self.assertEqual(state["seq"], 1)
            workdir1 = root / "runs" / state["run_dir"] / "work" / "bug-py-01"

            # 3) check 在起始代码上运行可见测试通过
            rc, chk_out, _ = _run_cli(["check"], root, mode_file)
            self.assertEqual(rc, 0, chk_out)

            # 4) 应用参考解并 submit；submit 只回"已提交"，不透露对错
            shutil.copy2(FIXTURES / "answers" / "bug-py-01" / "solution" / "src" / "calc.py", workdir1 / "src" / "calc.py")
            rc, sub_out, _ = _run_cli(["submit"], root, mode_file)
            self.assertEqual(rc, 0, sub_out)
            self.assertTrue(sub_out.startswith("已提交"))
            self.assertNotIn("pass", sub_out.lower())
            self.assertNotIn("通过", sub_out)

            # 5) 重复 submit 拒绝
            rc_dup, dup_out, _ = _run_cli(["submit"], root, mode_file)
            self.assertNotEqual(rc_dup, 0)
            self.assertTrue(dup_out.strip().splitlines()[-1].startswith("下一步："))

            # 6) 中途断掉后再执行 start 续跑并记录 starts
            rc, resume_out, _ = _run_cli(["start"], root, mode_file)
            self.assertEqual(rc, 0, resume_out)
            self.assertIn(state["marker"], resume_out)
            _, state = load_active_state(root)
            self.assertEqual(len(state["starts"]), 2)

            # 7) 第 2 题 review-py-01 用 check 验证格式后提交
            rc, out2, _ = _run_cli(["next"], root, mode_file)
            self.assertEqual(rc, 0)
            self.assertIn("LITMUS-TASK-review-py-01", out2)
            workdir2 = root / "runs" / state["run_dir"] / "work" / "review-py-01"
            shutil.copy2(FIXTURES / "answers" / "review-py-01" / "solution" / "review.json", workdir2 / "review.json")
            rc, chk2, _ = _run_cli(["check"], root, mode_file)
            self.assertEqual(rc, 0, chk2)
            rc, sub2, _ = _run_cli(["submit"], root, mode_file)
            self.assertEqual(rc, 0)
            self.assertTrue(sub2.startswith("已提交"))

            # 8) 再次 next 输出 ALL DONE
            rc, done_out, _ = _run_cli(["next"], root, mode_file)
            self.assertEqual(rc, 0)
            self.assertIn("ALL DONE", done_out)

            _, final_state = load_active_state(root)
            self.assertEqual(final_state["status"], "done")
            self.assertEqual(final_state["results"]["bug-py-01"]["status"], "pass")
            self.assertEqual(final_state["results"]["review-py-01"]["status"], "pass")

    def test_start_new_abandons_old_run_and_skip_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mode_file = _build_temp_litmus_repo(root)

            _run_cli(["start", "--quick"], root, mode_file)
            old_dir, old_state = load_active_state(root)
            _run_cli(["next"], root, mode_file)
            rc, skip_out, _ = _run_cli(["skip"], root, mode_file)
            self.assertEqual(rc, 0, skip_out)

            # status 不应泄露对错
            rc, st_out, _ = _run_cli(["status"], root, mode_file)
            self.assertEqual(rc, 0)
            self.assertIn("跳过", st_out)

            # --new 废弃旧测评并新开
            rc, new_out, _ = _run_cli(["start", "--new"], root, mode_file)
            self.assertEqual(rc, 0, new_out)
            old_after = json.loads((old_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(old_after["status"], "abandoned")
            _, cur_state = load_active_state(root)
            self.assertNotEqual(cur_state["run_dir"], old_state["run_dir"])
            self.assertEqual(cur_state["mode"], "full")


if __name__ == "__main__":
    unittest.main()
