"""统计学辅助计算：Wilson 置信区间。"""

import math
from typing import Tuple


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> Tuple[float, float]:
    """计算二项分布通过率的 Wilson 置信区间；样本数为 0 时返回 (0.0, 0.0)。"""
    if total < 0 or successes < 0 or successes > total:
        raise ValueError("非法参数: successes={}, total={}".format(successes, total))
    if total == 0:
        return 0.0, 0.0

    n = float(total)
    p = float(successes) / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n)) / denom
    low = max(0.0, center - half)
    high = min(1.0, center + half)
    return low, high
