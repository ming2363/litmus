"""历史对照。2023 年的交接缝规则只出现在这份报表里。"""

from typing import List, Sequence, Tuple

from wharfbook.legacy_fold import fold_handoff

Span = Tuple[int, int]


def handoff_view(spans: Sequence[Span]) -> List[Span]:
    return fold_handoff(list(spans))


def seam_count(spans: Sequence[Span]) -> int:
    """按旧规则折叠后，数首尾相接但仍分开的缝。"""
    folded = fold_handoff(list(spans))
    seams = 0
    for index in range(len(folded) - 1):
        if folded[index][1] == folded[index + 1][0]:
            seams += 1
    return seams


def compare_text(spans: Sequence[Span]) -> str:
    folded = handoff_view(spans)
    parts = ["{}-{}".format(start, end) for start, end in folded]
    body = "、".join(parts) if parts else "无"
    return "交接视图 {} 段，缝 {}。{}".format(len(folded), seam_count(spans), body)
