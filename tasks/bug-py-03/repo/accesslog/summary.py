"""按日志级别计数。"""

from typing import Dict

from accesslog.parser import parse_lines


def by_level(text: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in parse_lines(text):
        level = row["level"]
        counts[level] = counts.get(level, 0) + 1
    return counts


def slowest(text: str):
    """返回耗时最长的一行；没有日志时返回 None。"""
    rows = parse_lines(text)
    if not rows:
        return None
    return max(rows, key=lambda row: (row["duration_ms"], row["date"]))
