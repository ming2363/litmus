"""批次面单汇总与校验工具。"""

from collections import Counter
from typing import Any, Dict, List

from src.identifiers import extract_parcel_codes, is_valid_parcel_code, parse_parcel_code


def summarize_dispatch_log(log_text: str) -> Dict[str, Any]:
    """统计调度日志中各站点与带退换标运单数量。"""
    codes = extract_parcel_codes(log_text)
    site_counts: Counter = Counter()
    rework_codes: List[str] = []
    for code in codes:
        parsed = parse_parcel_code(code)
        if parsed is None:
            continue
        site_counts[parsed["site"]] += 1
        if parsed["suffix"] is not None:
            rework_codes.append(code)
    return {
        "total": len(codes),
        "codes": codes,
        "by_site": dict(sorted(site_counts.items())),
        "rework_codes": rework_codes,
    }


def filter_valid_codes(candidates: List[str]) -> List[str]:
    """过滤出合法的运单编号。"""
    return [c for c in candidates if is_valid_parcel_code(c)]
