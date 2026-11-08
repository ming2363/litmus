"""费率基础规则与默认运价查询表。"""

from typing import Dict, Tuple

TIER_MULTIPLIER: Dict[str, float] = {
    "economy": 0.85,
    "standard": 1.0,
    "express": 1.45,
}

BASE_ROUTE_CENTS: Dict[Tuple[str, str], int] = {
    ("CN", "US"): 1800,
    ("CN", "DE"): 1600,
    ("CN", "JP"): 950,
    ("US", "DE"): 1400,
}


def default_rate_provider(origin: str, dest: str, tier: str) -> int:
    """根据起运地、目的地与服务等级返回基础首重运价（分）。"""
    base = BASE_ROUTE_CENTS.get((origin, dest), 1200)
    mult = TIER_MULTIPLIER[tier]
    return int(round(base * mult))
