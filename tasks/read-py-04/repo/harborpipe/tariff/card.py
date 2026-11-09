"""冷箱电费价卡。金额是分，电量是瓦时，温度偏离是十分之一摄氏度。"""

from typing import Dict, List, Tuple

# 货类 -> (基础分/小时, 每瓦时分, 超温加价分/小时, 允许偏离)
CARD: Dict[str, Tuple[int, int, int, int]] = {
    "冻肉": (120, 4, 40, 15),
    "冻鱼": (130, 4, 45, 12),
    "香蕉": (80, 3, 20, 8),
    "药品": (200, 6, 80, 5),
    "巧克力": (90, 3, 25, 10),
    "冰淇淋": (160, 5, 60, 8),
    "血浆": (240, 7, 100, 3),
    "疫苗": (260, 8, 120, 2),
    "鲜花": (70, 2, 15, 10),
    "奶酪": (110, 4, 30, 6),
}


def quote(cargo: str, hours: int, watt_hours: int, worst_delta: int) -> int:
    if cargo not in CARD:
        raise KeyError(cargo)
    if type(hours) is not int or hours < 0:
        raise ValueError("小时数不合法")
    if type(watt_hours) is not int or watt_hours < 0:
        raise ValueError("瓦时不合法")
    if type(worst_delta) is not int or worst_delta < 0:
        raise ValueError("偏离不合法")
    base, per_wh, extra, limit = CARD[cargo]
    fee = hours * base + watt_hours * per_wh
    if worst_delta > limit:
        fee += hours * extra
    return fee


def explain(cargo: str, hours: int, watt_hours: int, worst_delta: int) -> str:
    amount = quote(cargo, hours, watt_hours, worst_delta)
    return "{} {} 小时 {} 瓦时，费用 {} 分".format(cargo, hours, watt_hours, amount)


def cheapest(hours: int, watt_hours: int) -> str:
    ranked = sorted(CARD, key=lambda cargo: (quote(cargo, hours, watt_hours, 0), cargo))
    return ranked[0]


def over_limit(cargo: str, worst_delta: int) -> bool:
    return worst_delta > CARD[cargo][3]


def breakdown(cargo: str, hours: int, watt_hours: int, worst_delta: int) -> List[Tuple[str, int]]:
    base, per_wh, extra, limit = CARD[cargo]
    rows = [("基础", hours * base), ("电量", watt_hours * per_wh)]
    if worst_delta > limit:
        rows.append(("超温", hours * extra))
    return rows
