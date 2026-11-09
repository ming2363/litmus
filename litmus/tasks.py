"""manifest.json 与 task.json 加载和字段一致性校验。"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from litmus.paths import get_repo_root, manifest_path, tasks_dir

VALID_LANGS: Tuple[str, ...] = ("java", "python", "none")
VALID_DIFFICULTIES: Tuple[str, ...] = ("easy", "medium", "hard", "long")
VALID_GRADERS: Tuple[str, ...] = ("tests", "terminal", "tool_call", "read_code", "review")


class TaskValidationError(Exception):
    """题目清单或元数据校验失败。"""


@dataclass(frozen=True)
class Manifest:
    version: int
    order: Tuple[str, ...]
    quick: Tuple[str, ...]


@dataclass(frozen=True)
class TaskSpec:
    id: str
    dimension: str
    lang: str
    difficulty: str
    title: str
    ref_minutes: float
    grader: str
    allowed_paths: Tuple[str, ...]
    max_changed_lines: Optional[int]
    answer_file: Optional[str]
    task_dir: Path
    prompt_path: Path
    repo_dir: Path


def _read_json(path: Path, label: str) -> Any:
    if not path.is_file():
        raise TaskValidationError("{} 不存在: {}".format(label, path))
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TaskValidationError("{} 解析失败 ({}): {}".format(label, path, exc))


def _ensure_str_list(val: Any, field_name: str, allow_empty: bool = False) -> List[str]:
    if not isinstance(val, list) or not all(isinstance(x, str) and x.strip() for x in val):
        raise TaskValidationError("字段 {} 必须是非空字符串列表".format(field_name))
    if not allow_empty and len(val) == 0:
        raise TaskValidationError("字段 {} 不能为空".format(field_name))
    return list(val)


def load_manifest(root: Optional[Path] = None) -> Manifest:
    """加载并校验 tasks/manifest.json。"""
    mpath = manifest_path(root)
    data = _read_json(mpath, "manifest.json")
    if not isinstance(data, dict):
        raise TaskValidationError("manifest.json 必须是 JSON 对象")

    version = data.get("version")
    if isinstance(version, bool) or version != 1:
        raise TaskValidationError("manifest.json 的 version 必须为 1")

    order = _ensure_str_list(data.get("order"), "order", allow_empty=False)
    if len(set(order)) != len(order):
        raise TaskValidationError("manifest.json 的 order 存在重复题号")

    quick = _ensure_str_list(data.get("quick"), "quick", allow_empty=True)
    if len(set(quick)) != len(quick):
        raise TaskValidationError("manifest.json 的 quick 存在重复题号")

    order_set = set(order)
    missing = [tid for tid in quick if tid not in order_set]
    if missing:
        raise TaskValidationError("quick 包含不在 order 中的题号: {}".format(", ".join(missing)))

    return Manifest(version=1, order=tuple(order), quick=tuple(quick))


def load_task(task_id: str, root: Optional[Path] = None) -> TaskSpec:
    """加载并校验单个题目目录及 task.json。"""
    tdir = tasks_dir(root) / task_id
    if not tdir.is_dir():
        raise TaskValidationError("题目目录不存在: {}".format(tdir))

    data = _read_json(tdir / "task.json", "task.json ({})".format(task_id))
    if not isinstance(data, dict):
        raise TaskValidationError("task.json 必须是 JSON 对象: {}".format(task_id))

    raw_id = data.get("id")
    if not isinstance(raw_id, str) or raw_id != task_id:
        raise TaskValidationError("task.json 的 id ({}) 与目录名 ({}) 不一致".format(raw_id, task_id))

    dimension = data.get("dimension")
    if not isinstance(dimension, str) or not dimension.strip():
        raise TaskValidationError("题目 {} 的 dimension 不能为空".format(task_id))

    lang = data.get("lang")
    if lang not in VALID_LANGS:
        raise TaskValidationError("题目 {} 的 lang 非法: {}".format(task_id, lang))

    difficulty = data.get("difficulty")
    if difficulty not in VALID_DIFFICULTIES:
        raise TaskValidationError("题目 {} 的 difficulty 非法: {}".format(task_id, difficulty))

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        raise TaskValidationError("题目 {} 的 title 不能为空".format(task_id))

    ref_minutes = data.get("ref_minutes")
    if isinstance(ref_minutes, bool) or not isinstance(ref_minutes, (int, float)) or ref_minutes <= 0:
        raise TaskValidationError("题目 {} 的 ref_minutes 必须为正数".format(task_id))

    grader = data.get("grader")
    if grader not in VALID_GRADERS:
        raise TaskValidationError("题目 {} 的 grader 非法: {}".format(task_id, grader))

    raw_allowed = data.get("allowed_paths")
    if grader == "tests":
        allowed_paths = tuple(_ensure_str_list(raw_allowed, "allowed_paths", allow_empty=False))
    elif raw_allowed is None:
        allowed_paths = ()
    else:
        allowed_paths = tuple(_ensure_str_list(raw_allowed, "allowed_paths", allow_empty=True))

    max_changed_lines = data.get("max_changed_lines")
    if max_changed_lines is not None:
        if isinstance(max_changed_lines, bool) or not isinstance(max_changed_lines, int) or max_changed_lines <= 0:
            raise TaskValidationError("题目 {} 的 max_changed_lines 必须为正整数".format(task_id))

    answer_file = data.get("answer_file")
    if grader in ("tool_call", "read_code", "review"):
        if not isinstance(answer_file, str) or not answer_file.strip():
            raise TaskValidationError("答案题 {} 必须提供非空 answer_file".format(task_id))
    elif answer_file is not None and (not isinstance(answer_file, str) or not answer_file.strip()):
        raise TaskValidationError("题目 {} 的 answer_file 非法".format(task_id))

    prompt_path = tdir / "prompt.md"
    if not prompt_path.is_file():
        raise TaskValidationError("题目 {} 缺少 prompt.md".format(task_id))

    repo_dir = tdir / "repo"
    if not repo_dir.is_dir():
        raise TaskValidationError("题目 {} 缺少 repo/ 目录".format(task_id))

    return TaskSpec(
        id=task_id,
        dimension=dimension.strip(),
        lang=lang,
        difficulty=difficulty,
        title=title.strip(),
        ref_minutes=float(ref_minutes),
        grader=grader,
        allowed_paths=allowed_paths,
        max_changed_lines=max_changed_lines,
        answer_file=answer_file.strip() if isinstance(answer_file, str) else None,
        task_dir=tdir,
        prompt_path=prompt_path,
        repo_dir=repo_dir,
    )


def load_all_tasks(root: Optional[Path] = None) -> Tuple[Manifest, Dict[str, TaskSpec]]:
    """加载 manifest 与全部题目，校验 manifest 与 tasks/ 子目录一一对应。"""
    manifest = load_manifest(root)
    troot = tasks_dir(root)
    dir_ids = sorted(
        entry.name
        for entry in troot.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    )
    order_set = set(manifest.order)
    dir_set = set(dir_ids)

    missing_dirs = sorted(order_set - dir_set)
    if missing_dirs:
        raise TaskValidationError("manifest 中存在缺失目录的题号: {}".format(", ".join(missing_dirs)))

    extra_dirs = sorted(dir_set - order_set)
    if extra_dirs:
        raise TaskValidationError("tasks/ 中存在未列入 manifest 的目录: {}".format(", ".join(extra_dirs)))

    tasks: Dict[str, TaskSpec] = {}
    for tid in manifest.order:
        tasks[tid] = load_task(tid, root)
    return manifest, tasks


def get_task_order(mode: str, manifest: Manifest) -> List[str]:
    """根据测评模式返回本次题号顺序列表。"""
    if mode == "full":
        return list(manifest.order)
    if mode == "quick":
        if not manifest.quick:
            raise TaskValidationError("manifest.json 的 quick 列表为空")
        return list(manifest.quick)
    raise TaskValidationError("未知测评模式: {}".format(mode))


def compute_bank_version(root: Optional[Path] = None) -> str:
    """计算题库版本摘要：对 tasks/manifest.json 和全部 tasks/*/task.json 的字节（按路径排序）算 SHA-256 前 12 位。"""
    repo = get_repo_root(root)
    tdir = tasks_dir(root)
    m_path = manifest_path(root)
    file_paths: List[Path] = []
    if m_path.is_file():
        file_paths.append(m_path)
    if tdir.is_dir():
        for p in tdir.glob("*/task.json"):
            if p.is_file():
                file_paths.append(p)
    file_paths.sort(key=lambda p: p.relative_to(repo).as_posix())
    hasher = hashlib.sha256()
    for p in file_paths:
        hasher.update(p.read_bytes())
    return hasher.hexdigest()[:12]
