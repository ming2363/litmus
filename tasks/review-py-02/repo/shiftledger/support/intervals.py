"""半开整数区间 [start, end) 的合并与扣减。"""


def _clean(intervals):
    out = []
    for item in intervals:
        if len(item) != 2:
            raise ValueError("pair")
        start, end = item
        if end < start:
            raise ValueError("order")
        if end == start:
            continue
        out.append((start, end))
    return out


def merge(intervals):
    """合并重叠或相邻区间。"""
    ordered = sorted(_clean(intervals))
    if not ordered:
        return []
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        last_s, last_e = merged[-1]
        if start <= last_e:
            merged[-1] = (last_s, max(last_e, end))
        else:
            merged.append((start, end))
    return merged


def subtract(base, cuts):
    """从 base 中挖去 cuts。"""
    current = merge(base)
    for cut_s, cut_e in merge(cuts):
        nxt = []
        for start, end in current:
            if cut_e <= start or cut_s >= end:
                nxt.append((start, end))
                continue
            if cut_s > start:
                nxt.append((start, cut_s))
            if cut_e < end:
                nxt.append((cut_e, end))
        current = nxt
    return current


def total_length(intervals):
    """合并后的总长度。"""
    return sum(end - start for start, end in merge(intervals))


def overlap_length(left, right):
    """两组区间的交集长度。"""
    a = merge(left)
    b = merge(right)
    i = 0
    j = 0
    total = 0
    while i < len(a) and j < len(b):
        start = max(a[i][0], b[j][0])
        end = min(a[i][1], b[j][1])
        if end > start:
            total += end - start
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return total
