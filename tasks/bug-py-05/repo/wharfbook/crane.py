"""岸桥可及范围。岸桥按米定位，不改占用分钟。"""

from typing import Dict, List, Optional, Sequence, Tuple

from wharfbook.lanes import YardMap, north_yard

# 岸桥号 -> (起点米, 终点米, 每分钟可移动米)
CRANES: Dict[str, Tuple[int, int, int]] = {
    "QC1": (0, 400, 30),
    "QC2": (180, 620, 30),
    "QC3": (500, 980, 24),
    "QC4": (860, 1400, 24),
}

# 巷道在码头线上的投影，半开米。
LANE_MARKS: Dict[str, Tuple[int, int]] = {
    "A": (0, 280),
    "B": (280, 560),
    "C": (560, 880),
    "D": (880, 1090),
    "E": (1090, 1270),
    "F": (560, 820),
    "G": (820, 1120),
    "H": (1120, 1280),
}


def crane_ids() -> List[str]:
    return sorted(CRANES)


def covers_mark(crane_id: str, mark_m: int) -> bool:
    start, end, _speed = CRANES[crane_id]
    return start <= mark_m < end


def cranes_for_lane(code: str) -> List[str]:
    start, end = LANE_MARKS[code]
    found = []
    for crane_id, (left, right, _speed) in CRANES.items():
        if left < end and right > start:
            found.append(crane_id)
    return sorted(found)


def travel_minutes(crane_id: str, origin_m: int, target_m: int) -> int:
    _start, _end, speed = CRANES[crane_id]
    if speed <= 0:
        raise ValueError("岸桥速度不合法")
    distance = abs(target_m - origin_m)
    return (distance + speed - 1) // speed


def assignment(codes: Sequence[str]) -> Dict[str, str]:
    """每条巷道挑编号最小的可及岸桥。没有可及岸桥的巷道不出现。"""
    chosen: Dict[str, str] = {}
    for code in codes:
        options = cranes_for_lane(code)
        if options:
            chosen[code] = options[0]
    return chosen


def boom_conflict(left_crane: str, right_crane: str, gap_m: int) -> bool:
    """两台岸桥的工作区间相距不足 gap_m 时视为动臂冲突。"""
    if gap_m < 0:
        raise ValueError("间距不能为负")
    left = CRANES[left_crane]
    right = CRANES[right_crane]
    separated = left[1] <= right[0] or right[1] <= left[0]
    if separated:
        hole = max(right[0] - left[1], left[0] - right[1])
        return hole < gap_m
    return True


def reachable_lanes(crane_id: str, yard: Optional[YardMap] = None) -> List[str]:
    host = yard if yard is not None else north_yard()
    return [code for code in host.codes() if code in LANE_MARKS and cranes_for_lane(code).count(crane_id)]
