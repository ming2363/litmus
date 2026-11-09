"""班组人力。人数和资质，不决定占用怎么合并。"""

from typing import Dict, List, Sequence, Tuple

from wharfbook.shifts import gang_on, shift_of

# 资质 -> 该班组在册人数里具备此资质的人。键是 (班组, 资质)。
HEADCOUNT: Dict[Tuple[str, str], int] = {}
for _gang, _base in (("甲", 6), ("乙", 5), ("丙", 7), ("丁", 4)):
    HEADCOUNT[(_gang, "引航")] = _base
    HEADCOUNT[(_gang, "系缆")] = _base + 2
    HEADCOUNT[(_gang, "冷藏")] = max(1, _base - 3)
    HEADCOUNT[(_gang, "值班长")] = 1

QUALIFICATIONS = ("引航", "系缆", "冷藏", "值班长")


def available(minute: int, qualification: str) -> int:
    if qualification not in QUALIFICATIONS:
        raise ValueError("未知资质")
    gang = gang_on(minute // 1440, shift_of(minute))
    return HEADCOUNT[(gang, qualification)]


def covered(minute: int, need: Sequence[Tuple[str, int]]) -> bool:
    for qualification, count in need:
        if type(count) is not int or count < 0:
            raise ValueError("需求人数不合法")
        if available(minute, qualification) < count:
            return False
    return True


def shortage(minute: int, need: Sequence[Tuple[str, int]]) -> List[Tuple[str, int]]:
    missing = []
    for qualification, count in need:
        gap = count - available(minute, qualification)
        if gap > 0:
            missing.append((qualification, gap))
    return missing


def week_minimum(qualification: str) -> Tuple[str, int]:
    """七天三班里，该资质在册人数最少的 (班组, 人数)。并列取班组名较小者。"""
    best_gang = None
    best_count = None
    for day in range(7):
        for shift_name in ("早班", "中班", "夜班"):
            gang = gang_on(day, shift_name)
            count = HEADCOUNT[(gang, qualification)]
            if best_count is None or count < best_count or (count == best_count and gang < best_gang):
                best_gang = gang
                best_count = count
    return best_gang, best_count  # type: ignore[return-value]
