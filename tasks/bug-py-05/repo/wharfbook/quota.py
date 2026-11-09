"""冷藏插头配额。按巷道插头数和同时在线的箱数计算，不读占用账本。"""

from typing import Dict, List, Sequence, Tuple

from wharfbook.lanes import plug_budget

# 货类每箱需要的插头数。
PLUGS_PER_BOX = {
    "冷藏": 1,
    "冷冻": 2,
    "果蔬": 1,
    "干货": 0,
}


def demand(boxes: Sequence[Tuple[str, int]]) -> int:
    total = 0
    for kind, count in boxes:
        if kind not in PLUGS_PER_BOX:
            raise ValueError("未知冷藏类别")
        if type(count) is not int or count < 0:
            raise ValueError("箱数必须是非负整数")
        total += PLUGS_PER_BOX[kind] * count
    return total


def admits(lane_codes: Sequence[str], boxes: Sequence[Tuple[str, int]]) -> bool:
    return demand(boxes) <= plug_budget(lane_codes)


def shortfall(lane_codes: Sequence[str], boxes: Sequence[Tuple[str, int]]) -> int:
    gap = demand(boxes) - plug_budget(lane_codes)
    return gap if gap > 0 else 0


def split_across(lane_codes: Sequence[str], boxes: Sequence[Tuple[str, int]]) -> Dict[str, int]:
    """按巷道插头比例分摊需求，余数分给编号较小的巷道。"""
    if not lane_codes:
        raise ValueError("至少一条巷道")
    needed = demand(boxes)
    weights = {code: plug_budget([code]) for code in lane_codes}
    total_plugs = sum(weights.values())
    if total_plugs <= 0:
        raise ValueError("这些巷道没有插头")
    raw = {code: needed * weights[code] // total_plugs for code in lane_codes}
    leftover = needed - sum(raw.values())
    for code in sorted(lane_codes):
        if leftover == 0:
            break
        raw[code] += 1
        leftover -= 1
    return raw


def overloaded(lane_codes: Sequence[str], boxes: Sequence[Tuple[str, int]]) -> List[str]:
    share = split_across(lane_codes, boxes)
    return sorted(code for code, used in share.items() if used > plug_budget([code]))
