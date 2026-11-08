"""工作目录与起始代码目录比对：改动文件清单、allowed_paths 校验与改动行数统计。"""

import difflib
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Sequence

from litmus.paths import is_ignored_relpath


class DiffError(Exception):
    """目录比较失败（如存在不允许的符号链接）。"""


@dataclass(frozen=True)
class DiffSummary:
    added: List[str]
    modified: List[str]
    deleted: List[str]
    changed_files: List[str]
    changed_lines: int


def find_symlinks(base_dir: Path) -> List[str]:
    """检查目录内是否存在符号链接（忽略 .git）。"""
    root = Path(base_dir)
    found: List[str] = []
    if not root.exists():
        return found
    for dirpath, dirnames, filenames in os.walk(str(root), followlinks=False):
        cur = Path(dirpath)
        dirnames[:] = sorted(d for d in dirnames if d != ".git")
        for dname in dirnames:
            dpath = cur / dname
            if dpath.is_symlink():
                found.append(dpath.relative_to(root).as_posix())
        for fname in sorted(filenames):
            fpath = cur / fname
            if fpath.is_symlink():
                found.append(fpath.relative_to(root).as_posix())
    return sorted(found)


def _scan_files(base_dir: Path) -> Dict[str, Path]:
    root = Path(base_dir)
    result: Dict[str, Path] = {}
    for dirpath, dirnames, filenames in os.walk(str(root), followlinks=False):
        cur = Path(dirpath)
        kept_dirs: List[str] = []
        for dname in sorted(dirnames):
            rel_dir = (cur / dname).relative_to(root).as_posix() + "/x"
            if not is_ignored_relpath(rel_dir):
                kept_dirs.append(dname)
        dirnames[:] = kept_dirs
        for fname in sorted(filenames):
            fpath = cur / fname
            rel = fpath.relative_to(root).as_posix()
            if not is_ignored_relpath(rel):
                result[rel] = fpath
    return result


def _normalize_lines(raw: Optional[bytes]) -> List[str]:
    if raw is None:
        return []
    text = raw.decode("utf-8", errors="replace")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return [line.rstrip() for line in text.splitlines()]


def count_file_changed_lines(old_bytes: Optional[bytes], new_bytes: Optional[bytes]) -> int:
    """统一换行符并去掉行尾空白后，用 difflib 统计改动行数（replace 取较大变更侧）。"""
    old_lines = _normalize_lines(old_bytes)
    new_lines = _normalize_lines(new_bytes)
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    total = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            total += j2 - j1
        elif tag == "delete":
            total += i2 - i1
        elif tag == "replace":
            total += max(i2 - i1, j2 - j1)
    return total


def compare_dirs(repo_dir: Path, workdir: Path) -> DiffSummary:
    """比较起始代码与工作目录，忽略构建产物与工具文件。"""
    symlinks = find_symlinks(workdir)
    if symlinks:
        raise DiffError("工作目录存在不允许的符号链接: {}".format(", ".join(symlinks)))

    repo_files = _scan_files(repo_dir)
    work_files = _scan_files(workdir)

    repo_keys = set(repo_files.keys())
    work_keys = set(work_files.keys())

    added = sorted(work_keys - repo_keys)
    deleted = sorted(repo_keys - work_keys)
    modified: List[str] = []
    changed_lines = 0

    for rel in added:
        changed_lines += count_file_changed_lines(None, work_files[rel].read_bytes())

    for rel in deleted:
        changed_lines += count_file_changed_lines(repo_files[rel].read_bytes(), None)

    for rel in sorted(repo_keys & work_keys):
        old_raw = repo_files[rel].read_bytes()
        new_raw = work_files[rel].read_bytes()
        if old_raw != new_raw:
            modified.append(rel)
            changed_lines += count_file_changed_lines(old_raw, new_raw)

    changed_files = sorted(set(added) | set(modified) | set(deleted))
    return DiffSummary(
        added=added,
        modified=modified,
        deleted=deleted,
        changed_files=changed_files,
        changed_lines=changed_lines,
    )


def _glob_to_regex(pattern: str) -> str:
    pat = pattern.replace("\\", "/").lstrip("./")
    parts = ["^"]
    i = 0
    n = len(pat)
    while i < n:
        if pat[i : i + 3] == "**/":
            parts.append("(?:.+/)?")
            i += 3
        elif pat[i : i + 2] == "**":
            parts.append(".*")
            i += 2
        elif pat[i] == "*":
            parts.append("[^/]*")
            i += 1
        elif pat[i] == "?":
            parts.append("[^/]")
            i += 1
        else:
            parts.append(re.escape(pat[i]))
            i += 1
    parts.append("$")
    return "".join(parts)


def glob_match(rel_path: str, pattern: str) -> bool:
    """按 POSIX 路径语义匹配 glob 规则（* 不跨目录，** 跨目录）。"""
    norm_path = rel_path.replace("\\", "/").lstrip("./")
    norm_pat = pattern.replace("\\", "/").lstrip("./")
    if norm_path == norm_pat:
        return True
    regex = _glob_to_regex(norm_pat)
    return re.match(regex, norm_path) is not None


def check_allowed_paths(
    changed_files: Sequence[str], allowed_patterns: Sequence[str]
) -> List[str]:
    """返回不在 allowed_paths 范围内的越界修改文件列表。"""
    violations: List[str] = []
    for rel in changed_files:
        if not any(glob_match(rel, pat) for pat in allowed_patterns):
            violations.append(rel)
    return sorted(violations)


def is_visible_test_file(rel_path: str) -> bool:
    """判断起始代码中的文件是否属于可见测试文件。"""
    norm = rel_path.replace("\\", "/").lstrip("./")
    posix = PurePosixPath(norm)
    parts = posix.parts
    if "tests" in parts[:-1] or "test" in parts[:-1]:
        return True
    name = posix.name
    if name.startswith("test_") and name.endswith(".py"):
        return True
    if name.endswith("_test.py"):
        return True
    if name.endswith("Test.java") or name.endswith("Tests.java"):
        return True
    if name.startswith("Test") and name.endswith(".java"):
        return True
    return False
