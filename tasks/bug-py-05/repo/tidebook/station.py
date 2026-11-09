"""验潮站与调和常数。高度单位是厘米，时间是计划周内的分钟。"""

from typing import Dict, List, Sequence, Tuple

Constituent = Tuple[str, float, float]


STATIONS: Dict[str, Dict[str, object]] = {
    "NB-01": {
        "name": "北港外栏",
        "datum_cm": 142,
        "timezone_shift_min": 0,
        "constituents": (
            ("M2", 118.0, 92.0),
            ("S2", 46.0, 128.0),
            ("K1", 27.0, 214.0),
            ("O1", 21.0, 176.0),
        ),
    },
    "NB-04": {
        "name": "北港内港池",
        "datum_cm": 151,
        "timezone_shift_min": 0,
        "constituents": (
            ("M2", 96.0, 101.0),
            ("S2", 38.0, 140.0),
            ("K1", 24.0, 220.0),
            ("O1", 18.0, 181.0),
        ),
    },
    "NB-07": {
        "name": "东防波堤",
        "datum_cm": 136,
        "timezone_shift_min": 6,
        "constituents": (
            ("M2", 124.0, 88.0),
            ("S2", 51.0, 121.0),
            ("N2", 22.0, 74.0),
            ("K1", 29.0, 209.0),
        ),
    },
}

# 分潮角速度，度/分钟。只保留调度台用到的四项。
SPEED_DEG_PER_MIN = {
    "M2": 28.9841042 / 60.0,
    "S2": 30.0 / 60.0,
    "N2": 28.4397295 / 60.0,
    "K1": 15.0410686 / 60.0,
    "O1": 13.9430356 / 60.0,
}


def station_names() -> List[str]:
    return sorted(STATIONS)


def datum_cm(station_id: str) -> int:
    row = STATIONS.get(station_id)
    if row is None:
        raise KeyError(station_id)
    return int(row["datum_cm"])


def constituents_of(station_id: str) -> Sequence[Constituent]:
    row = STATIONS.get(station_id)
    if row is None:
        raise KeyError(station_id)
    return row["constituents"]  # type: ignore[return-value]


def _angle(speed: float, minute: int, phase: float) -> float:
    # 用整数度近似，避免各解释器的三角库差异；调用方只比较高低潮次序。
    turned = (speed * minute + phase) % 360.0
    quadrant = int(turned // 90.0) % 4
    local = turned - quadrant * 90.0
    # 0..90 映射到 0..1 的折线，足够判断潮位升降。
    rise = local / 90.0
    if quadrant == 0:
        return rise
    if quadrant == 1:
        return 1.0 - rise
    if quadrant == 2:
        return -rise
    return rise - 1.0


def height_cm(station_id: str, minute: int) -> int:
    """返回该分钟相对测站零点的潮高，厘米。"""
    row = STATIONS.get(station_id)
    if row is None:
        raise KeyError(station_id)
    shifted = minute + int(row["timezone_shift_min"])
    total = float(row["datum_cm"])
    for name, amplitude, phase in row["constituents"]:  # type: ignore[union-attr]
        speed = SPEED_DEG_PER_MIN[name]
        total += amplitude * _angle(speed, shifted, phase)
    return int(round(total))


def extrema(station_id: str, start: int, end: int, step: int = 10) -> List[Tuple[int, int, str]]:
    """在半开区间里按步长找潮位转折，返回 (分钟, 厘米, high|low)。"""
    if step <= 0 or start >= end:
        raise ValueError("潮位扫描区间不合法")
    samples = []
    cursor = start
    while cursor < end:
        samples.append((cursor, height_cm(station_id, cursor)))
        cursor += step
    found: List[Tuple[int, int, str]] = []
    for index in range(1, len(samples) - 1):
        prev_h = samples[index - 1][1]
        cur_m, cur_h = samples[index]
        next_h = samples[index + 1][1]
        if cur_h >= prev_h and cur_h > next_h:
            found.append((cur_m, cur_h, "high"))
        elif cur_h <= prev_h and cur_h < next_h:
            found.append((cur_m, cur_h, "low"))
    return found


def under_keel_ok(station_id: str, minute: int, draft_cm: int, margin_cm: int) -> bool:
    if draft_cm <= 0 or margin_cm < 0:
        raise ValueError("吃水或富余水深不合法")
    return height_cm(station_id, minute) >= draft_cm + margin_cm
