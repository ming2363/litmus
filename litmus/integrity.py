"""防篡改校验（git HEAD、已跟踪文件干净度、禁止文件）与审计日志读写。"""

import fcntl
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from litmus.paths import FORBIDDEN_FILES, audit_log_path, get_repo_root, runs_dir
from litmus.state import now_iso, parse_iso

VALID_AUDIT_OPS: Tuple[str, ...] = ("grade", "unseal", "selftest", "seal")
_PROTECTED_PATHS: Tuple[str, ...] = ("litmus.py", "litmus", "tasks", "answers")
_FORBIDDEN_UPPER = {name.upper() for name in FORBIDDEN_FILES}


def is_git_repo(root: Optional[Path] = None) -> bool:
    repo = get_repo_root(root)
    proc = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def get_git_head(root: Optional[Path] = None) -> Optional[str]:
    repo = get_repo_root(root)
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    sha = proc.stdout.strip()
    return sha or None


def get_dirty_paths(
    paths: Optional[Sequence[str]] = None,
    include_untracked: bool = True,
    root: Optional[Path] = None,
) -> List[str]:
    repo = get_repo_root(root)
    cmd = ["git", "status", "--porcelain"]
    if not include_untracked:
        cmd.append("--untracked-files=no")
    else:
        cmd.append("--untracked-files=all")
    if paths:
        cmd.append("--")
        cmd.extend(paths)
    proc = subprocess.run(
        cmd,
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ["<git status 执行失败: {}>".format(proc.stderr.strip())]
    lines = [line.rstrip("\n") for line in proc.stdout.splitlines() if line.strip()]
    return lines


def find_forbidden_files(root: Optional[Path] = None) -> List[str]:
    """扫描仓库任意位置是否存在 AGENTS.md / CLAUDE.md / GEMINI.md。"""
    repo = get_repo_root(root)
    found: List[str] = []
    for dirpath, dirnames, filenames in os.walk(str(repo), followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d != ".git")
        cur = Path(dirpath)
        for fname in sorted(filenames):
            if fname.upper() in _FORBIDDEN_UPPER:
                found.append((cur / fname).relative_to(repo).as_posix())
    return sorted(found)


def append_audit(
    op: str,
    task_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    root: Optional[Path] = None,
) -> None:
    """追加一条加密/解密操作记录到 runs/audit.log（使用文件锁防止并发写交错）。"""
    if op not in VALID_AUDIT_OPS:
        raise ValueError("未知审计操作类型: {}".format(op))
    rdir = runs_dir(root)
    rdir.mkdir(parents=True, exist_ok=True)
    apath = audit_log_path(root)
    entry = {
        "at": now_iso(),
        "op": op,
        "task": task_id,
        "run_dir": run_dir,
    }
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    fd = os.open(str(apath), os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def read_audit_log(root: Optional[Path] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
    apath = audit_log_path(root)
    if not apath.is_file():
        return [], []
    entries: List[Dict[str, Any]] = []
    errors: List[str] = []
    for idx, raw_line in enumerate(apath.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            errors.append("audit.log 第 {} 行 JSON 损坏".format(idx))
            continue
        if not isinstance(obj, dict):
            errors.append("audit.log 第 {} 行格式非对象".format(idx))
            continue
        entries.append(obj)
    return entries, errors


def check_audit_during_run(
    created_at: str, run_dir_name: str, root: Optional[Path] = None
) -> List[str]:
    """检查测评开始后是否存在非本次判分触发的解密操作。"""
    entries, parse_errors = read_audit_log(root)
    reasons: List[str] = list(parse_errors)
    start_dt = parse_iso(created_at)

    for entry in entries:
        raw_at = entry.get("at")
        if not isinstance(raw_at, str):
            reasons.append("audit.log 存在缺少时间戳的异常记录")
            continue
        try:
            entry_dt = parse_iso(raw_at)
        except ValueError:
            reasons.append("audit.log 存在非法时间戳记录: {}".format(raw_at))
            continue
        if entry_dt < start_dt:
            continue
        op = entry.get("op")
        if op != "grade":
            reasons.append("测评期间检测到判分以外的操作: op={} task={} at={}".format(op, entry.get("task"), raw_at))
        elif entry.get("run_dir") != run_dir_name:
            reasons.append("测评期间检测到非本次测评的判分记录: run_dir={} at={}".format(entry.get("run_dir"), raw_at))
    return reasons


def check_run_integrity(expected_head: str, root: Optional[Path] = None) -> List[str]:
    """校验 git HEAD 未变、已跟踪文件干净、受保护路径无未跟踪修改、无禁止文件。"""
    reasons: List[str] = []
    if not is_git_repo(root):
        reasons.append("当前目录不是有效 git 仓库")
        return reasons

    current_head = get_git_head(root)
    if current_head != expected_head:
        reasons.append("git HEAD 发生变化: {} -> {}".format(expected_head, current_head))

    dirty_tracked = get_dirty_paths(paths=None, include_untracked=False, root=root)
    if dirty_tracked:
        reasons.append("已跟踪文件相对 HEAD 存在改动: {}".format("; ".join(dirty_tracked)))

    dirty_protected = get_dirty_paths(paths=_PROTECTED_PATHS, include_untracked=True, root=root)
    if dirty_protected:
        reasons.append("受保护目录存在未提交改动: {}".format("; ".join(dirty_protected)))

    forbidden = find_forbidden_files(root)
    if forbidden:
        reasons.append("检测到禁止文件: {}".format(", ".join(forbidden)))

    return reasons
