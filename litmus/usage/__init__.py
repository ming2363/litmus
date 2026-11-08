"""会话日志 token 与模型 ID 采集入口。"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from litmus.paths import get_repo_root


def safe_int(value) -> int:
    """把日志里的用量值转成整数；遇到非数字、空值或异常类型返回 0，不抛异常。

    设计要求：日志中个别坏字段只跳过该项，不能让整个工具的统计变成"未采集"。
    """
    if isinstance(value, bool):
        return 0
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        try:
            return int(float(value))
        except (TypeError, ValueError, OverflowError):
            return 0


@dataclass
class TokenBucket:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0

    def add(
        self,
        input_t: int = 0,
        output_t: int = 0,
        cache_read: int = 0,
        cache_write: int = 0,
        reasoning: int = 0,
    ) -> None:
        self.input_tokens += max(0, safe_int(input_t))
        self.output_tokens += max(0, safe_int(output_t))
        self.cache_read_tokens += max(0, safe_int(cache_read))
        self.cache_write_tokens += max(0, safe_int(cache_write))
        self.reasoning_tokens += max(0, safe_int(reasoning))

    def to_dict(self) -> Dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_write_tokens": self.cache_write_tokens,
            "reasoning_tokens": self.reasoning_tokens,
        }


@dataclass
class UsageSummary:
    collected: bool
    tool: str
    models: Dict[str, TokenBucket] = field(default_factory=dict)
    by_task: Dict[str, TokenBucket] = field(default_factory=dict)
    total: TokenBucket = field(default_factory=TokenBucket)
    note: str = ""


def normalize_task_ids(task_markers: Sequence[str]) -> List[str]:
    out: List[str] = []
    for item in task_markers:
        if item.startswith("LITMUS-TASK-"):
            out.append(item[len("LITMUS-TASK-"):])
        else:
            out.append(item)
    return out


def find_task_marker_in_text(text: str, task_ids: Sequence[str]) -> Optional[str]:
    """在文本中查找最后出现的已知题目标记 LITMUS-TASK-<id>。"""
    best_pos = -1
    best_id: Optional[str] = None
    for tid in task_ids:
        needle = "LITMUS-TASK-{}".format(tid)
        pos = text.rfind(needle)
        if pos > best_pos:
            best_pos = pos
            best_id = tid
    return best_id


def collect(
    marker: str,
    task_markers: Sequence[str],
    root: Optional[Path] = None,
    *,
    claude_dir: Optional[Path] = None,
    codex_dir: Optional[Path] = None,
    opencode_db: Optional[Path] = None
) -> UsageSummary:
    """按运行标记依次尝试解析 Claude Code / Codex / OpenCode 会话日志。"""
    from litmus.usage.claude import collect_claude
    from litmus.usage.codex import collect_codex
    from litmus.usage.opencode import collect_opencode

    repo = get_repo_root(root)
    task_ids = normalize_task_ids(task_markers)

    for fn in (
        lambda: collect_claude(marker, task_ids, repo, base_dir=claude_dir),
        lambda: collect_codex(marker, task_ids, base_dir=codex_dir),
        lambda: collect_opencode(marker, task_ids, db_path=opencode_db),
    ):
        try:
            res = fn()
        except Exception:
            res = None
        if res is not None and res.collected:
            return res

    return UsageSummary(
        collected=False,
        tool="unknown",
        models={},
        by_task={},
        total=TokenBucket(),
        note="未采集",
    )
