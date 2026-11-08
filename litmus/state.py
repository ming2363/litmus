"""测评状态管理：fcntl.flock 文件锁、同目录临时文件原子写入与 ACTIVE 指针。"""

import fcntl
import json
import os
import secrets
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from litmus.paths import STATE_FILENAME, active_file, lock_file_path, runs_dir


class StateError(Exception):
    """测评状态读写失败或状态损坏。"""


def now_iso() -> str:
    """返回带本地时区偏移的 ISO 8601 时间戳（兼容 Python 3.9）。"""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_iso(ts: str) -> datetime:
    """解析 ISO 8601 时间字符串，兼容 Python 3.9 不支持末尾 Z 的限制。"""
    cleaned = ts.strip()
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """先写入同目录临时文件并 fsync，再使用 os.replace 原子替换。"""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=str(target.parent),
            prefix=".tmp_{}_".format(target.name),
            suffix=".tmp",
            delete=False,
        ) as f:
            tmp_path = Path(f.name)
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(str(tmp_path), str(target))
        tmp_path = None
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()


def atomic_write_text(path: Path, text: str) -> None:
    """以 UTF-8 与 LF 换行原子写出文本文件。"""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    atomic_write_bytes(path, normalized.encode("utf-8"))


@contextmanager
def state_lock(root: Optional[Path] = None) -> Iterator[None]:
    """基于 fcntl.flock 的互斥锁上下文管理器；永不删除锁文件以保证 inode 稳定。"""
    rdir = runs_dir(root)
    rdir.mkdir(parents=True, exist_ok=True)
    lpath = lock_file_path(root)
    fd = os.open(str(lpath), os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def generate_run_dir_name() -> str:
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    return "{}-{}".format(stamp, secrets.token_hex(2))


def generate_run_marker() -> str:
    return "LITMUS-RUN-{}".format(secrets.token_hex(3))


def read_active_name(root: Optional[Path] = None) -> Optional[str]:
    apath = active_file(root)
    if not apath.is_file():
        return None
    name = apath.read_text(encoding="utf-8").strip()
    return name or None


def set_active_name(run_dir_name: Optional[str], root: Optional[Path] = None) -> None:
    apath = active_file(root)
    if run_dir_name is None:
        if apath.exists():
            apath.unlink()
        return
    atomic_write_text(apath, run_dir_name + "\n")


def load_state(run_dir: Path) -> Dict[str, Any]:
    spath = Path(run_dir) / STATE_FILENAME
    if not spath.is_file():
        raise StateError("状态文件不存在: {}".format(spath))
    try:
        data = json.loads(spath.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError("状态文件解析失败 ({}): {}".format(spath, exc))
    if not isinstance(data, dict):
        raise StateError("状态文件格式错误: {}".format(spath))
    return data


def save_state(run_dir: Path, state: Dict[str, Any]) -> None:
    spath = Path(run_dir) / STATE_FILENAME
    payload = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
    atomic_write_text(spath, payload)


def create_run(
    mode: str,
    head: str,
    order: List[str],
    root: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """创建新测评目录、初始化 state.json 并更新 runs/ACTIVE。"""
    rroot = runs_dir(root)
    rroot.mkdir(parents=True, exist_ok=True)
    run_name = generate_run_dir_name()
    while (rroot / run_name).exists():
        run_name = generate_run_dir_name()

    run_dir = rroot / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    created_at = now_iso()
    state: Dict[str, Any] = {
        "run_dir": run_name,
        "marker": generate_run_marker(),
        "mode": mode,
        "created_at": created_at,
        "finished_at": None,
        "head": head,
        "order": list(order),
        "current": None,
        "current_started_at": None,
        "seq": 0,
        "results": {},
        "starts": [{"at": created_at, "at_task": None}],
        "integrity_violations": [],
        "env": dict(env or {}),
        "status": "active",
    }
    save_state(run_dir, state)
    set_active_name(run_name, root)
    return run_dir, state


def load_active_state(root: Optional[Path] = None) -> Optional[Tuple[Path, Dict[str, Any]]]:
    """根据 runs/ACTIVE 加载最近一次测评目录与状态。"""
    name = read_active_name(root)
    if not name:
        return None
    run_dir = runs_dir(root) / name
    if not (run_dir / STATE_FILENAME).is_file():
        return None
    return run_dir, load_state(run_dir)


def has_active_run(root: Optional[Path] = None) -> Optional[str]:
    """检查 runs/ 下是否存在任意 status == 'active' 的测评，防止绕过 ACTIVE 指针。"""
    rroot = runs_dir(root)
    if not rroot.is_dir():
        return None
    active_name = read_active_name(root)
    if active_name:
        rdir = rroot / active_name
        if (rdir / STATE_FILENAME).is_file():
            st = load_state(rdir)
            if st.get("status") == "active":
                return active_name
    for entry in sorted(rroot.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        spath = entry / STATE_FILENAME
        if spath.is_file():
            st = load_state(entry)
            if st.get("status") == "active":
                return st.get("run_dir") or entry.name
    return None
