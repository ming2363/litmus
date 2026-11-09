"""2023 年交接规则的折叠，只给历史对照报表使用。"""

from typing import List, Sequence, Tuple

Span = Tuple[int, int]


def fold_handoff(spans: Sequence[Span]) -> List[Span]:
    """按交接缝保留首尾相接的段。"""
    ordered = sorted((start, end) for start, end in spans)
    if not ordered:
        return []
    folded: List[Span] = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = folded[-1]
        if start < last_end:
            if end > last_end:
                folded[-1] = (last_start, end)
        else:
            folded.append((start, end))
    return folded
