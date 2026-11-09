"""潮汐窗口的分钟折叠与挖除。"""

from typing import List, Sequence, Tuple

MinuteSpan = Tuple[int, int]


def check_minute(value: object) -> int:
    """读一个分钟编号。"""
    if type(value) is not int:
        raise ValueError("分钟编号必须是整数")
    return value


def check_span(item: object) -> MinuteSpan:
    """读一段潮汐窗口，返回新的元组。"""
    if not isinstance(item, tuple) or len(item) != 2:
        raise ValueError("区间必须是长度为 2 的元组")
    start = check_minute(item[0])
    end = check_minute(item[1])
    if start >= end:
        raise ValueError("区间必须满足 start < end")
    return (start, end)


def fold_minutes(spans: Sequence[MinuteSpan]) -> List[MinuteSpan]:
    """折叠一批潮汐窗口，返回新的列表。"""
    clean = [check_span(item) for item in spans]
    if not clean:
        return []
    ordered = sorted(clean)
    folded: List[MinuteSpan] = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = folded[-1]
        if start <= last_end:
            if end > last_end:
                folded[-1] = (last_start, end)
        else:
            folded.append((start, end))
    return folded


def cut_minutes(spans: Sequence[MinuteSpan], blocks: Sequence[MinuteSpan]) -> List[MinuteSpan]:
    """按封航窗口从潮汐窗口里挖去一段，返回新的列表。"""
    occupied = fold_minutes(spans)
    closed = fold_minutes(blocks)
    if not occupied or not closed:
        return list(occupied)
    kept: List[MinuteSpan] = []
    block_index = 0
    block_count = len(closed)
    for start, end in occupied:
        cursor = start
        while block_index < block_count and closed[block_index][1] <= cursor:
            block_index += 1
        probe = block_index
        while probe < block_count and closed[probe][0] < end:
            block_start, block_end = closed[probe]
            if block_start > cursor:
                kept.append((cursor, min(block_start, end)))
            cursor = max(cursor, block_end)
            if cursor >= end:
                break
            probe += 1
        if cursor < end:
            kept.append((cursor, end))
    return kept
