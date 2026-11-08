"""跨境运费与税费报价核心计算模块。"""

import math
from typing import Any, Callable, Dict, List, Optional

from src.rules import TIER_MULTIPLIER, default_rate_provider


def compute_tariff(
    origin: str,
    dest: str,
    weight_grams: int,
    tier: str = "standard",
    overrides: Optional[Dict[str, float]] = None,
    *,
    rate_provider: Optional[Callable[[str, str, str], int]] = None,
) -> Dict[str, Any]:
    """计算指定线路与重量的运费报价明细。"""
    if not isinstance(origin, str) or not origin.strip():
        raise ValueError("origin 不能为空")
    if not isinstance(dest, str) or not dest.strip():
        raise ValueError("dest 不能为空")
    if isinstance(weight_grams, bool) or not isinstance(weight_grams, int) or weight_grams <= 0:
        raise ValueError("weight_grams 必须是正整数")
    if tier not in TIER_MULTIPLIER:
        raise ValueError("不支持的服务等级: {!r}".format(tier))

    norm_origin = origin.strip().upper()
    norm_dest = dest.strip().upper()
    provider = rate_provider if rate_provider is not None else default_rate_provider

    base_cents = int(provider(norm_origin, norm_dest, tier))
    if base_cents < 0:
        raise ValueError("基础运价不能为负: {}".format(base_cents))

    extra_blocks = max(0, math.ceil((weight_grams - 500) / 500.0))
    surcharge_cents = extra_blocks * (320 if tier == "express" else 200)
    subtotal = base_cents + surcharge_cents

    tags: List[str] = ["tier:{}".format(tier)]
    discount_cents = 0
    if overrides and tier in overrides:
        factor = float(overrides[tier])
        if factor <= 0.0 or factor > 2.0:
            raise ValueError("overrides 系数必须在 (0, 2.0] 内: {}".format(factor))
        adjusted = int(round(subtotal * factor))
        discount_cents = subtotal - adjusted
        tags.append("override:applied")

    total_cents = subtotal - discount_cents
    return {
        "origin": norm_origin,
        "dest": norm_dest,
        "tier": tier,
        "weight_grams": weight_grams,
        "base_cents": base_cents,
        "surcharge_cents": surcharge_cents,
        "discount_cents": discount_cents,
        "total_cents": total_cents,
        "tags": tags,
    }
