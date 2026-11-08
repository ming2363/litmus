"""做题端命令行实现：start / next / check / submit / skip / status / report（严禁提及出题工具）。"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from litmus.crypto import CryptoError, unseal_to
from litmus.diffcheck import find_symlinks
from litmus.envcheck import run_env_checks
from litmus.graders import grade
from litmus.integrity import append_audit, check_run_integrity, get_git_head
from litmus.paths import answers_dir, find_repo_root, grade_root_dir
from litmus.report import generate_and_write_report
from litmus.state import (
    create_run,
    load_active_state,
    now_iso,
    parse_iso,
    save_state,
    state_lock,
)
from litmus.tasks import TaskSpec, get_task_order, load_manifest, load_task
from litmus.testexec import CompileError, TestTimeoutError, run_tests


def _copy_repo_to_work(repo_dir: Path, workdir: Path) -> None:
    if workdir.exists():
        shutil.rmtree(str(workdir))
    workdir.mkdir(parents=True, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(str(repo_dir), followlinks=False):
        cur = Path(dirpath)
        dirnames[:] = sorted(d for d in dirnames if d != ".git")
        for dname in dirnames:
            (workdir / (cur / dname).relative_to(repo_dir)).mkdir(parents=True, exist_ok=True)
        for fname in sorted(filenames):
            fpath = cur / fname
            target = workdir / fpath.relative_to(repo_dir)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(fpath), str(target))


def _format_task_prompt(task: TaskSpec, workdir: Path, seq: int, total: int) -> str:
    prompt_body = task.prompt_path.read_text(encoding="utf-8").rstrip()
    lines = [
        "LITMUS-TASK-{}".format(task.id),
        "进度: 第 {}/{} 题".format(seq, total),
        "题号: {} | 维度: {} | 难度: {} | 语言: {} | 标题: {}".format(
            task.id, task.dimension, task.difficulty, task.lang, task.title
        ),
        "工作目录: {}".format(workdir.resolve()),
    ]
    if task.answer_file:
        lines.append("答案文件: 请将结果写入工作目录根下的 {}".format(task.answer_file))
    lines.extend([
        "-" * 60,
        prompt_body,
        "-" * 60,
        "下一步：在工作目录完成本题（可用 python3 litmus.py check 自测），完成后执行 python3 litmus.py submit",
    ])
    return "\n".join(lines)


def _cmd_start(
    args: argparse.Namespace,
    root: Path,
    ai_relay_mode_file: Optional[Path] = None,
) -> int:
    with state_lock(root):
        env_res = run_env_checks(root, ai_relay_mode_file=ai_relay_mode_file)
        if not env_res.ok:
            print("环境与干净度检查未通过，无法开始测评：")
            for item in env_res.items:
                if not item.passed:
                    print("- [失败] {}: {}".format(item.name, item.detail))
                    if item.fix_hint:
                        print("  修复方法: {}".format(item.fix_hint))
            print("下一步：按上述提示修复问题后，重新执行 python3 litmus.py start")
            return 1

        active = load_active_state(root)
        if active is not None and active[1].get("status") == "active":
            run_dir, state = active
            if args.new:
                state["status"] = "abandoned"
                state["finished_at"] = now_iso()
                save_state(run_dir, state)
            else:
                state.setdefault("starts", []).append(
                    {"at": now_iso(), "at_task": state.get("current")}
                )
                save_state(run_dir, state)
                done_cnt = len(state.get("results", {}))
                total_cnt = len(state.get("order", []))
                print("继续未完成的测评（模式: {}，进度: {}/{}）".format(state["mode"], done_cnt, total_cnt))
                print("运行标记: {}".format(state["marker"]))
                print("规则提醒：只看 tasks/ 当前题目与分配的工作目录，不要打开 answers/，不要修改 litmus.py 和 litmus/。")
                print("下一步：执行 python3 litmus.py next")
                return 0

        mode = "quick" if args.quick else "full"
        manifest = load_manifest(root)
        order = get_task_order(mode, manifest)
        head = get_git_head(root) or ""
        _, new_state = create_run(mode, head, order, root=root, env=env_res.env_info)
        print("已创建新测评（模式: {}，共 {} 题）".format(mode, len(order)))
        print("运行标记: {}".format(new_state["marker"]))
        print("做题规则：只看 tasks/ 当前题目和分配给你的工作目录；不要打开 answers/，不要修改 litmus.py 和 litmus/；不要中途停下。")
        print("下一步：执行 python3 litmus.py next")
        return 0


def _cmd_next(root: Path) -> int:
    with state_lock(root):
        active = load_active_state(root)
        if active is None:
            print("当前没有进行中的测评。")
            print("下一步：执行 python3 litmus.py start")
            return 1
        run_dir, state = active
        status = state.get("status")
        if status == "done":
            print("ALL DONE")
            print("下一步：执行 python3 litmus.py report")
            return 0
        if status != "active":
            print("当前测评状态为 {}，无法继续发题。".format(status))
            print("下一步：执行 python3 litmus.py start")
            return 1

        cur_id = state.get("current")
        if cur_id is None:
            results = state.get("results", {})
            remaining = [tid for tid in state.get("order", []) if tid not in results]
            if not remaining:
                state["status"] = "done"
                state["finished_at"] = now_iso()
                save_state(run_dir, state)
                print("ALL DONE")
                print("下一步：执行 python3 litmus.py report")
                return 0
            cur_id = remaining[0]
            task = load_task(cur_id, root)
            workdir = run_dir / "work" / cur_id
            _copy_repo_to_work(task.repo_dir, workdir)
            state["current"] = cur_id
            state["current_started_at"] = now_iso()
            state["seq"] = int(state.get("seq", 0)) + 1
            save_state(run_dir, state)
        else:
            task = load_task(cur_id, root)
            workdir = run_dir / "work" / cur_id
            if not workdir.is_dir():
                _copy_repo_to_work(task.repo_dir, workdir)

        print(_format_task_prompt(task, workdir, int(state["seq"]), len(state["order"])))
        return 0


def _validate_answer_format(task: TaskSpec, workdir: Path) -> Optional[str]:
    answer_name = task.answer_file or "answer.json"
    fpath = workdir / answer_name
    if fpath.is_symlink() or not fpath.is_file():
        return "缺少答案文件: {}".format(answer_name)
    try:
        data = json.loads(fpath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return "JSON 格式不合法 ({}): {}".format(answer_name, exc)

    if task.grader == "tool_call":
        if not isinstance(data, list):
            return "{} 必须是调用对象列表（无调用时写 []）".format(answer_name)
        for idx, item in enumerate(data):
            if not isinstance(item, dict) or not isinstance(item.get("name"), str):
                return "第 {} 条调用缺少字符串字段 name".format(idx + 1)
            if "args" in item and not isinstance(item["args"], dict):
                return "第 {} 条调用的 args 必须是对象".format(idx + 1)
    elif task.grader == "review":
        if not isinstance(data, list):
            return "{} 必须是审查意见对象列表".format(answer_name)
        if len(data) > 10:
            return "审查条目数 {} 超过上限 10".format(len(data))
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                return "第 {} 条审查意见必须是对象".format(idx + 1)
            if not isinstance(item.get("file"), str) or not item["file"].strip():
                return "第 {} 条审查意见缺少 file".format(idx + 1)
            line = item.get("line")
            if isinstance(line, bool) or not isinstance(line, int) or line < 1:
                return "第 {} 条审查意见缺少正整数 line".format(idx + 1)
            if not isinstance(item.get("category"), str) or not item["category"].strip():
                return "第 {} 条审查意见缺少 category".format(idx + 1)
    return None


def _cmd_check(root: Path) -> int:
    with state_lock(root):
        active = load_active_state(root)
        if active is None or active[1].get("status") != "active":
            print("当前没有进行中的测评。")
            print("下一步：执行 python3 litmus.py start")
            return 1
        run_dir, state = active
        cur_id = state.get("current")
        if not cur_id:
            print("当前没有待做题目。")
            print("下一步：执行 python3 litmus.py next")
            return 1
        task = load_task(cur_id, root)
        workdir = run_dir / "work" / cur_id

        if task.grader == "tests":
            try:
                outcomes = run_tests(task.lang, workdir)
            except (CompileError, TestTimeoutError) as exc:
                print("自测失败：{}".format(exc))
                print("下一步：修复问题后重新运行 python3 litmus.py check，或确认后执行 python3 litmus.py submit")
                return 1
            total = len(outcomes)
            passed = sum(1 for o in outcomes.values() if o.status == "pass")
            print("可见测试完成：通过 {}/{}".format(passed, total))
            for tid in sorted(outcomes.keys()):
                o = outcomes[tid]
                if o.status != "pass":
                    print("- [{}] {}: {}".format(o.status, o.id, o.message))
            print("下一步：确认无误后执行 python3 litmus.py submit")
            return 0 if (total > 0 and passed == total) else 1

        if task.grader == "terminal":
            symlinks = find_symlinks(workdir)
            if symlinks:
                print("工作目录存在不允许的符号链接：{}".format(", ".join(symlinks)))
                print("下一步：清理符号链接后执行 python3 litmus.py submit")
                return 1
            print("终端实操题不提供自动检查脚本，请核对工作目录 {} 内的最终状态。".format(workdir.resolve()))
            print("下一步：确认无误后执行 python3 litmus.py submit")
            return 0

        err = _validate_answer_format(task, workdir)
        if err is not None:
            print("答案格式校验失败：{}".format(err))
            print("下一步：修正答案文件格式后重新执行 python3 litmus.py check")
            return 1
        print("答案格式校验通过（仅检查 JSON 结构，不判对错）。")
        print("下一步：执行 python3 litmus.py submit")
        return 0


def _calc_elapsed(started_at: Optional[str], submitted_at: str) -> float:
    if not started_at:
        return 0.0
    delta = (parse_iso(submitted_at) - parse_iso(started_at)).total_seconds()
    return round(max(0.0, delta), 3)


def _cmd_submit(root: Path) -> int:
    with state_lock(root):
        active = load_active_state(root)
        if active is None or active[1].get("status") != "active":
            print("当前没有进行中的测评。")
            print("下一步：执行 python3 litmus.py start")
            return 1
        run_dir, state = active
        cur_id = state.get("current")
        if not cur_id:
            print("当前没有可提交的题目（请勿重复提交）。")
            print("下一步：执行 python3 litmus.py next")
            return 1
        if cur_id in state.get("results", {}):
            print("题目 {} 已提交，每题只能提交一次。".format(cur_id))
            print("下一步：执行 python3 litmus.py next")
            return 1

        task = load_task(cur_id, root)
        workdir = run_dir / "work" / cur_id
        # 耗时从 next 到开始判分，不含判分时间
        submitted_at = now_iso()
        elapsed_s = _calc_elapsed(state.get("current_started_at"), submitted_at)

        integrity_errs = check_run_integrity(state.get("head", ""), root=root)
        if integrity_errs:
            state.setdefault("integrity_violations", []).extend(integrity_errs)

        g_root = grade_root_dir(run_dir)
        g_dir = g_root / cur_id
        bundle_dir = g_dir / "_bundle"
        enc_file = answers_dir(root) / "{}.grade.enc".format(cur_id)
        try:
            append_audit("grade", task_id=cur_id, run_dir=state["run_dir"], root=root)
            unseal_to(enc_file, bundle_dir)
            res = grade(task, workdir, g_dir, bundle_dir)
        except CryptoError as exc:
            print("判分解密失败：{}".format(exc))
            print("下一步：执行 python3 litmus.py status")
            return 1
        finally:
            shutil.rmtree(str(g_dir), ignore_errors=True)
            if g_root.is_dir() and not any(g_root.iterdir()):
                g_root.rmdir()

        state.setdefault("results", {})[cur_id] = {
            "status": "pass" if res.passed else "fail",
            "reasons": res.reasons,
            "merge_veto": res.merge_veto,
            "elapsed_s": elapsed_s,
            "seq": int(state.get("seq", 0)),
            "submitted_at": submitted_at,
            "extra": res.extra,
        }
        state["current"] = None
        state["current_started_at"] = None

        all_done = all(tid in state["results"] for tid in state.get("order", []))
        if all_done:
            state["status"] = "done"
            state["finished_at"] = now_iso()
        save_state(run_dir, state)

        print("已提交")
        print("下一步：执行 python3 litmus.py next")
        return 0


def _cmd_skip(root: Path) -> int:
    with state_lock(root):
        active = load_active_state(root)
        if active is None or active[1].get("status") != "active":
            print("当前没有进行中的测评。")
            print("下一步：执行 python3 litmus.py start")
            return 1
        run_dir, state = active
        cur_id = state.get("current")
        if not cur_id:
            print("当前没有可跳过的题目。")
            print("下一步：执行 python3 litmus.py next")
            return 1

        submitted_at = now_iso()
        elapsed_s = _calc_elapsed(state.get("current_started_at"), submitted_at)
        state.setdefault("results", {})[cur_id] = {
            "status": "skipped",
            "reasons": ["跳过"],
            "merge_veto": False,
            "elapsed_s": elapsed_s,
            "seq": int(state.get("seq", 0)),
            "submitted_at": submitted_at,
            "extra": {},
        }
        state["current"] = None
        state["current_started_at"] = None
        if all(tid in state["results"] for tid in state.get("order", [])):
            state["status"] = "done"
            state["finished_at"] = now_iso()
        save_state(run_dir, state)

        print("已跳过当前题（按不通过计分）")
        print("下一步：执行 python3 litmus.py next")
        return 0


def _cmd_status(root: Path) -> int:
    with state_lock(root):
        active = load_active_state(root)
        if active is None:
            print("暂无测评记录。")
            print("下一步：执行 python3 litmus.py start")
            return 0
        _, state = active
        results: Dict[str, Dict] = state.get("results", {})
        total = len(state.get("order", []))
        done = len(results)
        skipped = sum(1 for r in results.values() if r.get("status") == "skipped")
        print("测评目录: {} | 模式: {} | 状态: {}".format(state["run_dir"], state["mode"], state["status"]))
        print("运行标记: {}".format(state["marker"]))
        print("进度: 已完成 {}/{} 题（含跳过 {} 题）".format(done, total, skipped))
        if state.get("current"):
            print("当前题目: {}".format(state["current"]))
            print("下一步：完成当前题后执行 python3 litmus.py submit")
        elif state.get("status") == "done":
            print("下一步：执行 python3 litmus.py report")
        else:
            print("下一步：执行 python3 litmus.py next")
        return 0


def _cmd_report(root: Path, usage_kwargs: Optional[Dict[str, Any]] = None) -> int:
    with state_lock(root):
        active = load_active_state(root)
        if active is None:
            print("当前没有可生成报告的测评记录。")
            print("下一步：执行 python3 litmus.py start")
            return 1
        run_dir, state = active
        _, md_text, md_path, json_path = generate_and_write_report(
            run_dir, state, root=root, usage_kwargs=usage_kwargs
        )
        print(md_text, end="")
        print("报告文件已写入：")
        print("- {}".format(md_path))
        print("- {}".format(json_path))
        print("下一步：测评报告已生成，请将报告内容原样提交给测评发起人")
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="litmus.py",
        description="litmus 编程能力测评做题工具",
    )
    sub = parser.add_subparsers(dest="command")
    p_start = sub.add_parser("start", help="环境检查并新建或续跑测评")
    p_start.add_argument("--quick", action="store_true", help="使用快速模式题单")
    p_start.add_argument("--new", action="store_true", help="放弃当前未完成测评并新开一次")
    sub.add_parser("next", help="发放下一题")
    sub.add_parser("check", help="自测当前题可见测试或答案格式")
    sub.add_parser("submit", help="提交并判分当前题")
    sub.add_parser("skip", help="放弃当前题并按不通过计分")
    sub.add_parser("status", help="查看当前测评进度")
    sub.add_parser("report", help="汇总成绩并写入 reports/ 目录")
    return parser


def main(
    argv: Optional[List[str]] = None,
    root: Optional[Path] = None,
    ai_relay_mode_file: Optional[Path] = None,
    usage_kwargs: Optional[Dict[str, Any]] = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = root if root is not None else find_repo_root()

    if args.command == "start":
        return _cmd_start(args, repo_root, ai_relay_mode_file=ai_relay_mode_file)
    if args.command == "next":
        return _cmd_next(repo_root)
    if args.command == "check":
        return _cmd_check(repo_root)
    if args.command == "submit":
        return _cmd_submit(repo_root)
    if args.command == "skip":
        return _cmd_skip(repo_root)
    if args.command == "status":
        return _cmd_status(repo_root)
    if args.command == "report":
        return _cmd_report(repo_root, usage_kwargs=usage_kwargs)

    parser.print_help()
    print("下一步：执行 python3 litmus.py start")
    return 0
