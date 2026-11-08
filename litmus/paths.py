"""仓库路径定位、目录常量与忽略规则。"""

from pathlib import Path, PurePosixPath
from typing import Optional, Tuple

REPO_ROOT: Path = Path(__file__).resolve().parent.parent

FORBIDDEN_FILES: Tuple[str, ...] = ("AGENTS.md", "CLAUDE.md", "GEMINI.md")

IGNORE_PATTERNS: Tuple[str, ...] = (
    "*.class",
    "out/",
    "build/",
    "target/",
    "__pycache__/",
    "*.pyc",
    ".pytest_cache/",
    ".git/",
    ".DS_Store",
)

_IGNORE_DIR_NAMES: Tuple[str, ...] = (
    "out",
    "build",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".git",
)

RUNS_DIRNAME = "runs"
REPORTS_DIRNAME = "reports"
TASKS_DIRNAME = "tasks"
ANSWERS_DIRNAME = "answers"
MANIFEST_FILENAME = "manifest.json"
ACTIVE_FILENAME = "ACTIVE"
AUDIT_LOG_FILENAME = "audit.log"
STATE_FILENAME = "state.json"
LOCK_FILENAME = ".litmus.lock"
GRADE_WORKDIR_NAME = ".grade"


def find_repo_root(start: Optional[Path] = None) -> Path:
    """从起始路径向上查找包含 litmus.py 或 .git 的仓库根目录。"""
    cur = (start or Path.cwd()).resolve()
    if cur.is_file():
        cur = cur.parent
    for candidate in (cur,) + tuple(cur.parents):
        if (candidate / "litmus.py").is_file() or (candidate / ".git").exists():
            return candidate
    return REPO_ROOT


def get_repo_root(root: Optional[Path] = None) -> Path:
    """返回指定根目录或默认仓库根目录。"""
    if root is None:
        return REPO_ROOT
    return Path(root).resolve()


def tasks_dir(root: Optional[Path] = None) -> Path:
    return get_repo_root(root) / TASKS_DIRNAME


def manifest_path(root: Optional[Path] = None) -> Path:
    return tasks_dir(root) / MANIFEST_FILENAME


def answers_dir(root: Optional[Path] = None) -> Path:
    return get_repo_root(root) / ANSWERS_DIRNAME


def runs_dir(root: Optional[Path] = None) -> Path:
    return get_repo_root(root) / RUNS_DIRNAME


def reports_dir(root: Optional[Path] = None) -> Path:
    return get_repo_root(root) / REPORTS_DIRNAME


def runners_dir() -> Path:
    """始终返回 litmus 包自带的运行器目录，不从工作目录取。"""
    return Path(__file__).resolve().parent / "runners"


def active_file(root: Optional[Path] = None) -> Path:
    return runs_dir(root) / ACTIVE_FILENAME


def audit_log_path(root: Optional[Path] = None) -> Path:
    return runs_dir(root) / AUDIT_LOG_FILENAME


def lock_file_path(root: Optional[Path] = None) -> Path:
    return runs_dir(root) / LOCK_FILENAME


def grade_root_dir(run_dir: Path) -> Path:
    return Path(run_dir) / GRADE_WORKDIR_NAME


def strip_rel_prefix(rel_path: str) -> str:
    """去掉相对路径开头的 ./ 与 /，保留 .DS_Store、.git 这类点文件名。

    不能用 str.lstrip("./")：它按字符集合剥离，会把 .DS_Store 变成 DS_Store。
    """
    cleaned = rel_path.replace("\\", "/")
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    while cleaned.startswith("/"):
        cleaned = cleaned[1:]
    return cleaned


def is_ignored_relpath(rel_path: str) -> bool:
    """判断相对路径是否属于构建产物或工具忽略文件。"""
    cleaned = strip_rel_prefix(rel_path)
    if not cleaned:
        return False
    parts = PurePosixPath(cleaned).parts
    for part in parts:
        if part in _IGNORE_DIR_NAMES:
            return True
    name = parts[-1]
    if name == ".DS_Store":
        return True
    if name.endswith(".class") or name.endswith(".pyc"):
        return True
    return False
