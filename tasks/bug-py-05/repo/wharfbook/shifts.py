"""班组钟点。这里的边界只用于排班，不参与占用归并。"""

from typing import Dict, List, Optional, Tuple

# 半开分钟区间，相对周一 00:00。一天 1440 分钟，三班倒。
SHIFT_BOUNDS: Tuple[Tuple[str, int, int], ...] = (
    ("早班", 360, 840),
    ("中班", 840, 1320),
    ("夜班", 1320, 1800),
)

GANGS = ("甲", "乙", "丙", "丁")


def shift_of(minute: int) -> str:
    """返回分钟落在哪个班次名。跨过周日的负分钟先折回一周。"""
    day = 1440
    folded = minute % (7 * day)
    clock = folded % day
    # 夜班从 22:00 到次日 06:00，折到当天钟点后落在 0..360 或 1320..1440。
    if clock < 360 or clock >= 1320:
        return "夜班"
    if clock < 840:
        return "早班"
    return "中班"


def shift_window(minute: int) -> Tuple[int, int]:
    """返回包含该分钟的班次半开区间，起点按所在自然日对齐。"""
    day = 1440
    base = minute - (minute % day)
    if minute % day < 360:
        return (base - 120, base + 360)
    name = shift_of(minute)
    for label, start, end in SHIFT_BOUNDS:
        if label == name:
            # 早班、中班的表是当天钟点，要加到 base 上。
            if label == "夜班":
                return (base + 1320, base + 1800)
            return (base + start, base + end)
    raise RuntimeError(name)


def gang_on(day_index: int, shift_name: str) -> str:
    """四周一轮转。day_index 0 是计划周周一。"""
    if shift_name not in ("早班", "中班", "夜班"):
        raise ValueError("未知班次")
    if type(day_index) is not int:
        raise ValueError("日序号必须是整数")
    shift_index = {"早班": 0, "中班": 1, "夜班": 2}[shift_name]
    return GANGS[(day_index + shift_index) % len(GANGS)]


def roster(day_index: int) -> List[Tuple[str, str, int, int]]:
    rows = []
    for name, start, end in SHIFT_BOUNDS:
        begin = day_index * 1440 + start
        finish = day_index * 1440 + end
        if name == "夜班":
            begin = day_index * 1440 + 1320
            finish = begin + 480
        rows.append((name, gang_on(day_index, name), begin, finish))
    return rows


def overlap_minutes(left: Tuple[int, int], right: Tuple[int, int]) -> int:
    start = max(left[0], right[0])
    end = min(left[1], right[1])
    if start >= end:
        return 0
    return end - start


def busiest_gang(day_indexes: List[int]) -> Tuple[str, int]:
    """按班次分钟数累计，返回分钟最多的班组。并列时取名称较小的。"""
    totals: Dict[str, int] = {name: 0 for name in GANGS}
    for day_index in day_indexes:
        for _name, gang, begin, finish in roster(day_index):
            totals[gang] += finish - begin
    winner = sorted(totals, key=lambda gang: (-totals[gang], gang))[0]
    return winner, totals[winner]


def covers(minute: int, gang: str) -> bool:
    day_index = minute // 1440
    return gang_on(day_index, shift_of(minute)) == gang
