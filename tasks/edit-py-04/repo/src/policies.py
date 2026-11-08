"""运费模板、会员倍率与最大余数分摊辅助规则。"""

from typing import Dict, List, Sequence

MEMBER_DISCOUNT_BPS: Dict[str, int] = {
    "none": 0,
    "silver": 500,
    "gold": 1000,
}

REGION_SHIPPING_TABLE: Dict[str, Dict[str, int]] = {
    "CN_MAIN": {
        "base_cents": 1200,
        "free_threshold_cents": 9900,
        "remote_surcharge_cents": 0,
        "free_overweight_grams": 3000,
        "per_extra_kg_cents": 400,
    },
    "CN_REMOTE": {
        "base_cents": 1800,
        "free_threshold_cents": 19900,
        "remote_surcharge_cents": 800,
        "free_overweight_grams": 2000,
        "per_extra_kg_cents": 600,
    },
    "INTL": {
        "base_cents": 4500,
        "free_threshold_cents": 49900,
        "remote_surcharge_cents": 1500,
        "free_overweight_grams": 1500,
        "per_extra_kg_cents": 1200,
    },
}

LOYALTY_RATE_PER_100_CENTS: Dict[str, int] = {
    "none": 1,
    "silver": 2,
    "gold": 3,
}


def round_half_up_bps(amount_cents: int, bps: int) -> int:
    """按万分比（basis points）做四舍五入整分计算。"""
    if amount_cents <= 0 or bps <= 0:
        return 0
    return (amount_cents * bps + 5000) // 10000


def allocate_proportional(total_cents: int, weights: Sequence[int]) -> List[int]:
    """使用最大余数法（Hamilton 方法）将总额按权重精确分摊为整数分。"""
    n = len(weights)
    if n == 0 or total_cents <= 0:
        return [0] * n
    weight_sum = sum(w for w in weights if w > 0)
    if weight_sum <= 0:
        return [0] * n

    capped_total = min(total_cents, weight_sum)
    shares: List[int] = [0] * n
    remainders: List[tuple] = []
    allocated = 0

    for idx, w in enumerate(weights):
        if w <= 0:
            continue
        numer = capped_total * w
        base = numer // weight_sum
        rem = numer % weight_sum
        shares[idx] = base
        allocated += base
        remainders.append((-rem, idx))

    leftover = capped_total - allocated
    remainders.sort()
    for i in range(leftover):
        _, target_idx = remainders[i]
        shares[target_idx] += 1

    return shares
