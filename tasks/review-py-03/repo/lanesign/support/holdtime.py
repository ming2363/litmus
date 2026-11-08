"""停留时长分桶。"""


BUCKETS = (
    ("le_30", 0, 30),
    ("le_120", 30, 120),
    ("le_480", 120, 480),
    ("le_1440", 480, 1440),
    ("gt_1440", 1440, None),
)


def bucket_of(minutes):
    """返回桶名。负数拒绝。"""
    if minutes < 0:
        raise ValueError("minutes")
    for name, low, high in BUCKETS:
        if high is None and minutes >= low:
            return name
        if high is not None and low <= minutes < high:
            return name
    raise RuntimeError("bucket")


def tally(samples):
    """samples 是分钟列表。"""
    counts = {name: 0 for name, _low, _high in BUCKETS}
    for minutes in samples:
        counts[bucket_of(minutes)] += 1
    return counts


def dominant(samples):
    """数量最多的桶。并列时按 BUCKETS 声明顺序。"""
    counts = tally(samples)
    best = None
    best_n = -1
    for name, _low, _high in BUCKETS:
        if counts[name] > best_n:
            best = name
            best_n = counts[name]
    return best
