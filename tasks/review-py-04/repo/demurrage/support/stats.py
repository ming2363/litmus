"""小样本统计。"""


def mean(values):
    if not values:
        raise ValueError("empty")
    return sum(values) / float(len(values))


def median(values):
    if not values:
        raise ValueError("empty")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def percentile(values, pct):
    """最近秩。pct 取 0 到 100。"""
    if not values:
        raise ValueError("empty")
    if pct < 0 or pct > 100:
        raise ValueError("pct")
    ordered = sorted(values)
    if pct == 100:
        return ordered[-1]
    rank = int(round((len(ordered) - 1) * (pct / 100.0)))
    return ordered[rank]


def histogram(values, bins):
    """bins 为递增边界。返回每个桶的计数，右边界归入下一桶，最后一桶闭合。"""
    if len(bins) < 2:
        raise ValueError("bins")
    counts = [0 for _ in range(len(bins) - 1)]
    for value in values:
        placed = False
        for idx in range(len(bins) - 1):
            left, right = bins[idx], bins[idx + 1]
            last = idx == len(bins) - 2
            if (left <= value < right) or (last and value == right):
                counts[idx] += 1
                placed = True
                break
        if not placed:
            raise ValueError(value)
    return counts
