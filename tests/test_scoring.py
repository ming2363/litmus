"""综合分、效率系数与题库版本功能测试。"""

import tempfile
import unittest
from pathlib import Path

from litmus.report import render_markdown
from litmus.scoring import (
    DIFFICULTY_WEIGHTS,
    TOKEN_BUDGETS,
    compute_effective_tokens,
    compute_scores,
    compute_task_credit,
    compute_time_score,
    compute_token_score,
)
from litmus.tasks import VALID_DIFFICULTIES, compute_bank_version


class TestScoring(unittest.TestCase):
    def test_difficulty_weights_and_budgets(self):
        """覆盖：4 档难度权重与 token 预算配置。"""
        self.assertEqual(VALID_DIFFICULTIES, ("easy", "medium", "hard", "long"))
        self.assertEqual(DIFFICULTY_WEIGHTS["easy"], 1)
        self.assertEqual(DIFFICULTY_WEIGHTS["medium"], 2)
        self.assertEqual(DIFFICULTY_WEIGHTS["hard"], 3)
        self.assertEqual(DIFFICULTY_WEIGHTS["long"], 6)

        self.assertEqual(TOKEN_BUDGETS["easy"], 40000)
        self.assertEqual(TOKEN_BUDGETS["medium"], 100000)
        self.assertEqual(TOKEN_BUDGETS["hard"], 250000)
        self.assertEqual(TOKEN_BUDGETS["long"], 800000)

    def test_time_score_r_boundaries(self):
        """覆盖：r <= 1、r = 2 (0.8)、r = 4 (0.6)、r = 10 (0.6)。"""
        self.assertEqual(compute_time_score(0.2), 1.0)
        self.assertEqual(compute_time_score(1.0), 1.0)
        self.assertAlmostEqual(compute_time_score(2.0), 0.8, places=4)
        self.assertAlmostEqual(compute_time_score(4.0), 0.6, places=4)
        # r = 10 时触底下限 0.6
        self.assertAlmostEqual(compute_time_score(10.0), 0.6, places=4)

    def test_effective_tokens_calculation(self):
        """覆盖：计费等价 token = input + cache_write + output + 0.1 * cache_read。"""
        eff = compute_effective_tokens(
            input_tokens=1000,
            output_tokens=200,
            cache_read_tokens=5000,
            cache_write_tokens=300,
        )
        # 1000 + 300 + 200 + 0.1 * 5000 = 2000.0
        self.assertEqual(eff, 2000.0)

    def test_token_score_budget_ratios(self):
        """覆盖：token 预算内、2 倍预算 (0.75)、16 倍以上 (0.5)。"""
        # 预算内
        self.assertEqual(compute_token_score(30000, "easy"), 1.0)
        self.assertEqual(compute_token_score(40000, "easy"), 1.0)

        # 2 倍预算：1 - 0.25 * log2(2) = 0.75
        self.assertAlmostEqual(compute_token_score(80000, "easy"), 0.75, places=4)
        self.assertAlmostEqual(compute_token_score(200000, "medium"), 0.75, places=4)
        self.assertAlmostEqual(compute_token_score(500000, "hard"), 0.75, places=4)
        self.assertAlmostEqual(compute_token_score(1600000, "long"), 0.75, places=4)

        # 16 倍以上：1 - 0.25 * log2(16) = 0.0 -> 下限 0.5
        self.assertAlmostEqual(compute_token_score(640000, "easy"), 0.5, places=4)
        self.assertAlmostEqual(compute_token_score(2000000, "easy"), 0.5, places=4)

    def test_failed_tasks_excluded_from_time_and_token_score(self):
        """覆盖：做错的题不进时间分和 token 分。"""
        tasks = [
            {
                "id": "t1",
                "difficulty": "easy",
                "passed": True,
                "elapsed_s": 120,
                "ref_minutes": 1,   # r = 2.0 -> time_score = 0.8
                "effective_tokens": 40000,  # token_score = 1.0
            },
            {
                "id": "t2",
                "difficulty": "easy",
                "passed": False,
                "elapsed_s": 30,
                "ref_minutes": 1,   # r = 0.5, 若计入则会抬高时间分为 1.0
                "effective_tokens": 40000,
            },
        ]
        res = compute_scores(tasks, token_collected=True)
        # 正确性分：权重 1/2 -> 50.0
        self.assertEqual(res["correctness"], 50.0)
        # 做错的题不进时间分，时间分只由 t1 决定（0.8）
        self.assertEqual(res["time_score"], 0.8)
        self.assertEqual(res["token_score"], 1.0)
        # 逐题明细中未通过题的得分为 None
        self.assertIsNone(res["by_task"]["t2"]["time_score"])
        self.assertIsNone(res["by_task"]["t2"]["token_score"])

    def test_efficiency_coefficient_when_token_uncollected(self):
        """覆盖：token 未采集时的效率系数计算 (0.75 + 0.25 * 时间分)。"""
        tasks = [
            {
                "id": "t1",
                "difficulty": "medium",
                "passed": True,
                "elapsed_s": 120,
                "ref_minutes": 1,   # r = 2.0 -> time_score = 0.8
                "effective_tokens": 50000,
            }
        ]
        res = compute_scores(tasks, token_collected=False)
        self.assertFalse(res["token_collected"])
        self.assertIsNone(res["token_score"])
        self.assertEqual(res["time_score"], 0.8)
        # efficiency = 0.75 + 0.25 * 0.8 = 0.95
        self.assertEqual(res["efficiency"], 0.95)
        # composite = 100.0 * 0.95 = 95.0
        self.assertEqual(res["composite"], 95.0)

    def test_zero_passed_behavior(self):
        """覆盖：零通过时正确性分 0、综合分 0，时间分与 token 分为 None。"""
        tasks = [
            {
                "id": "t1",
                "difficulty": "hard",
                "passed": False,
                "elapsed_s": 60,
                "ref_minutes": 5,
            },
            {
                "id": "t2",
                "difficulty": "long",
                "passed": False,
                "elapsed_s": 120,
                "ref_minutes": 10,
            },
        ]
        res = compute_scores(tasks, token_collected=True)
        self.assertEqual(res["correctness"], 0.0)
        self.assertEqual(res["composite"], 0.0)
        self.assertIsNone(res["time_score"])
        self.assertIsNone(res["token_score"])
        self.assertIsNone(res["efficiency"])

    def test_hand_calculated_example(self):
        """覆盖：派单要求的手算样例核对。

        3 题：
        - easy 通过，r = 0.5，token 3 万
        - hard 通过，r = 2，token 50 万
        - medium 不通过

        推导：
        总权重 = 1 + 3 + 2 = 6
        通过权重 = 1 + 3 = 4
        正确性分 = 100 * 4 / 6 = 66.6667
        时间分 = (1.0 * 1 + 0.8 * 3) / 4 = 3.4 / 4 = 0.85
        token 分 = (1.0 * 1 + 0.75 * 3) / 4 = 3.25 / 4 = 0.8125
        效率系数 = 0.75 + 0.15 * 0.85 + 0.10 * 0.8125 = 0.95875
        综合分 = (400 / 6) * 0.95875 = 63.9167
        """
        tasks = [
            {
                "id": "easy-task",
                "difficulty": "easy",
                "passed": True,
                "elapsed_s": 30,
                "ref_minutes": 1,   # r = 0.5
                "effective_tokens": 30000,
            },
            {
                "id": "hard-task",
                "difficulty": "hard",
                "passed": True,
                "elapsed_s": 120,
                "ref_minutes": 1,   # r = 2.0
                "effective_tokens": 500000,
            },
            {
                "id": "medium-task",
                "difficulty": "medium",
                "passed": False,
                "elapsed_s": 60,
                "ref_minutes": 1,
                "effective_tokens": 20000,
            },
        ]
        res = compute_scores(tasks, token_collected=True)
        self.assertEqual(res["correctness"], 66.6667)
        self.assertEqual(res["time_score"], 0.85)
        self.assertEqual(res["token_score"], 0.8125)
        self.assertEqual(res["efficiency"], 0.9588)
        self.assertEqual(res["composite"], 63.9167)

    def test_markdown_render_composite_at_top_and_invalid_mark(self):
        """覆盖：Markdown 报告渲染综合分置顶、无效成绩标记、token 未采集注明与逐题表新列。"""
        # 1) 有效成绩
        mock_data_valid = {
            "report_id": "20261109-test-valid",
            "mode": "full",
            "run_dir": "/tmp/test",
            "marker": "LITMUS-RUN-test",
            "bank_version": "f77556ac5cc6",
            "litmus_commit": "abc1234",
            "started_at": "2026-11-09T10:00:00+08:00",
            "finished_at": "2026-11-09T10:10:00+08:00",
            "env": {"python_version": "3.11"},
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
            "by_dimension": [],
            "by_difficulty": [],
            "interruptions": {"resume_count": 0, "resumes": []},
            "usage": {
                "collected": True,
                "tool": "codex",
                "total": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_read_tokens": 20,
                    "cache_write_tokens": 10,
                    "reasoning_tokens": 5,
                },
                "models": {},
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
                }
            ],
        }
        md_valid = render_markdown(mock_data_valid)
        lines = md_valid.strip().splitlines()
        # 标题紧接着就是综合分
        self.assertEqual(lines[0], "# litmus 测评报告 (20261109-test-valid)")
        self.assertEqual(lines[2], "## 综合分：63.92")
        self.assertIn("正确性分：66.67 | 时间分：0.85 | token 分：0.81 | 效率系数：0.96", lines[3])
        self.assertIn("题库版本：`f77556ac5cc6`", md_valid)
        # 逐题表包含新列
        self.assertIn("| r | 时间得分 | 计费等价 token | token 得分 |", md_valid)
        self.assertIn("| 1 | task-01 | bug | easy | pass | 100% | 否 | 30.0 | 1.0 | 0.50 | 1.00 | 30000 | 1.00 | - |", md_valid)

        # 2) 成绩无效时：综合分旁标"无效"和原因
        mock_data_invalid = dict(mock_data_valid)
        mock_data_invalid["validity"] = {
            "valid": False,
            "reasons": ["检测到未加密答案文件", "git 工作区受污染"],
        }
        md_invalid = render_markdown(mock_data_invalid)
        self.assertIn("## 综合分：63.92（无效：检测到未加密答案文件；git 工作区受污染）", md_invalid)

        # 3) token 未采集时注明
        mock_data_no_tokens = dict(mock_data_valid)
        mock_data_no_tokens["score"] = {
            "composite": 80.0,
            "correctness": 80.0,
            "time_score": 1.0,
            "token_score": None,
            "efficiency": 1.0,
            "token_collected": False,
        }
        md_no_tokens = render_markdown(mock_data_no_tokens)
        self.assertIn("token 分：未采集（效率系数只用时间分）", md_no_tokens)

    def test_bank_version_sha256(self):
        """覆盖：题库版本 SHA-256 前 12 位计算。"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tdir = root / "tasks"
            (tdir / "t1").mkdir(parents=True)
            (tdir / "manifest.json").write_text('{"version": 1}\n', encoding="utf-8")
            (tdir / "t1" / "task.json").write_text('{"id": "t1"}\n', encoding="utf-8")

            v = compute_bank_version(root)
            self.assertEqual(len(v), 12)
            # 确定性检验：相同内容哈希一致
            v2 = compute_bank_version(root)
            self.assertEqual(v, v2)



class TestEfficiencyMissingData(unittest.TestCase):
    def test_passed_without_time_and_tokens_uses_floor(self):
        from litmus.scoring import compute_scores
        res = compute_scores([{"id": "a", "difficulty": "easy", "passed": True}], token_collected=False)
        self.assertAlmostEqual(res["efficiency"], 0.75)
        self.assertAlmostEqual(res["composite"], 75.0)


def _long_row(f2p_passed, f2p_total=52, p2p_passed=1016, p2p_total=1016, **kw):
    """构造一条没全过的长任务判分记录。"""
    row = {
        "id": kw.pop("id", "long-task"),
        "difficulty": kw.pop("difficulty", "long"),
        "grader": kw.pop("grader", "tests"),
        "status": kw.pop("status", "fail"),
        "passed": False,
        "merge_veto": kw.pop("merge_veto", False),
        "extra": {
            "f2p_passed": f2p_passed,
            "f2p_total": f2p_total,
            "p2p_passed": p2p_passed,
            "p2p_total": p2p_total,
        },
    }
    row.update(kw)
    return row


class TestLongTaskPartialCredit(unittest.TestCase):
    def test_long_task_gets_f2p_ratio(self):
        self.assertAlmostEqual(compute_task_credit(_long_row(51)), 51 / 52)
        self.assertAlmostEqual(compute_task_credit(_long_row(0)), 0.0)

    def test_passed_task_gets_full_credit(self):
        self.assertEqual(compute_task_credit({"difficulty": "easy", "passed": True}), 1.0)

    def test_p2p_regression_vetoes_partial_credit(self):
        self.assertEqual(compute_task_credit(_long_row(51, p2p_passed=1015)), 0.0)

    def test_merge_veto_vetoes_partial_credit(self):
        self.assertEqual(compute_task_credit(_long_row(51, merge_veto=True)), 0.0)

    def test_no_test_results_gets_zero(self):
        # 编译失败、整体超时：判分明细里没有用例计数
        row = _long_row(51)
        row["extra"] = {"changed_files": 3}
        self.assertEqual(compute_task_credit(row), 0.0)
        self.assertEqual(compute_task_credit(_long_row(51, status="skipped")), 0.0)
        self.assertEqual(compute_task_credit(_long_row(51, status="incomplete")), 0.0)

    def test_non_long_difficulty_stays_all_or_nothing(self):
        for diff in ("easy", "medium", "hard"):
            self.assertEqual(compute_task_credit(_long_row(51, difficulty=diff)), 0.0)

    def test_non_tests_grader_gets_zero(self):
        self.assertEqual(compute_task_credit(_long_row(51, grader="terminal")), 0.0)

    def test_bad_counts_get_zero(self):
        self.assertEqual(compute_task_credit(_long_row(0, f2p_total=0)), 0.0)
        self.assertEqual(compute_task_credit(_long_row(True, f2p_total=True)), 0.0)
        self.assertEqual(compute_task_credit(_long_row("51")), 0.0)

    def test_partial_credit_in_correctness_and_efficiency(self):
        """手算：easy 通过（r=0.5）+ 长任务 F2P 26/52（r=2）。

        总权重 = 1 + 6 = 7；得分权重 = 1 + 6 × 0.5 = 4
        正确性分 = 100 × 4 / 7 = 57.1429
        时间分按 权重 × 得分比例 平均 = (1.0 × 1 + 0.8 × 3) / 4 = 0.85
        token 未采集：效率系数 = 0.75 + 0.25 × 0.85 = 0.9625
        综合分 = 400 / 7 × 0.9625 = 55.0
        """
        tasks = [
            {"id": "e", "difficulty": "easy", "passed": True, "elapsed_s": 30, "ref_minutes": 1},
            _long_row(26, id="l", elapsed_s=7200, ref_minutes=60),
        ]
        res = compute_scores(tasks, token_collected=False)
        self.assertEqual(res["correctness"], 57.1429)
        self.assertEqual(res["time_score"], 0.85)
        self.assertEqual(res["efficiency"], 0.9625)
        self.assertEqual(res["composite"], 55.0)
        self.assertEqual(res["by_task"]["l"]["credit"], 0.5)
        self.assertEqual(res["by_task"]["l"]["time_score"], 0.8)
        self.assertEqual(res["by_task"]["e"]["credit"], 1.0)

    def test_only_partial_long_task_is_not_zero(self):
        res = compute_scores([_long_row(51, elapsed_s=600, ref_minutes=60)], token_collected=False)
        self.assertAlmostEqual(res["correctness"], round(100 * 51 / 52, 4))
        self.assertEqual(res["efficiency"], 1.0)

    def test_zero_credit_long_task_excluded_from_time(self):
        tasks = [
            {"id": "e", "difficulty": "easy", "passed": True, "elapsed_s": 30, "ref_minutes": 1},
            _long_row(51, id="l", p2p_passed=0, elapsed_s=99999, ref_minutes=60),
        ]
        res = compute_scores(tasks, token_collected=False)
        self.assertEqual(res["time_score"], 1.0)
        self.assertIsNone(res["by_task"]["l"]["time_score"])
        self.assertEqual(res["by_task"]["l"]["credit"], 0.0)

if __name__ == "__main__":
    unittest.main()
