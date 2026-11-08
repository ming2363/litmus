"""反复寻找一对能合并的区间，直到不再变化。"""

from typing import List, Sequence, Tuple


Interval = Tuple[int, int]


def merge_intervals(intervals: Sequence[Sequence[int]]) -> List[Interval]:
    """合并半开区间。相接的区间也会并成一段。"""
    items = _normalize(intervals)
    changed = True
    while changed:
        items, changed = _fold_once(items)
    items.sort()
    return items


def _fold_once(items: List[Interval]):
    """找到第一对相接或重叠的区间并合并，没有则原样返回。"""
    total = len(items)
    for left in range(total):
        for right in range(left + 1, total):
            first = items[left]
            second = items[right]
            if first[1] < second[0] or second[1] < first[0]:
                continue
            union = (min(first[0], second[0]), max(first[1], second[1]))
            merged = []
            for index, item in enumerate(items):
                if index == left:
                    merged.append(union)
                elif index == right:
                    continue
                else:
                    merged.append(item)
            return merged, True
    return items, False


def _normalize(intervals: Sequence[Sequence[int]]) -> List[Interval]:
    if isinstance(intervals, (str, bytes)) or not isinstance(intervals, Sequence):
        raise ValueError("区间列表不合法")
    normalized = []
    for item in intervals:
        if isinstance(item, (str, bytes)) or not isinstance(item, Sequence) or len(item) != 2:
            raise ValueError("每个区间必须有两个端点")
        start = _as_int(item[0])
        end = _as_int(item[1])
        if start >= end:
            raise ValueError("区间必须满足 start < end")
        normalized.append((start, end))
    return normalized


def _as_int(value) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("端点必须是整数")
    return value
