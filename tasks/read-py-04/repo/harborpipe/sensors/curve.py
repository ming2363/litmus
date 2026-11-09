"""探头校准。原始值是毫伏，输出是十分之一摄氏度。"""

from typing import Callable, List, Tuple

Point = Tuple[int, int]


def _lerp(points: List[Point], raw: int) -> int:
    if raw < points[0][0] or raw > points[-1][0]:
        raise ValueError("毫伏超出校准范围")
    for index in range(1, len(points)):
        left_raw, left_temp = points[index - 1]
        right_raw, right_temp = points[index]
        if left_raw <= raw <= right_raw:
            if right_raw == left_raw:
                return left_temp
            span = right_raw - left_raw
            return left_temp + (right_temp - left_temp) * (raw - left_raw) // span
    raise ValueError("校准段缺失")


def curve_p01(raw: int) -> int:
    return _lerp([(0, -300), (200, -180), (500, 0), (800, 200), (1000, 300)], raw)


def curve_p02(raw: int) -> int:
    return _lerp([(0, -280), (180, -160), (520, 10), (790, 190), (1000, 280)], raw)


def curve_p03(raw: int) -> int:
    return _lerp([(0, -320), (220, -200), (480, -10), (820, 210), (1000, 320)], raw)


def curve_p04(raw: int) -> int:
    return _lerp([(50, -250), (240, -100), (500, 20), (760, 160), (980, 260)], raw)


def curve_p05(raw: int) -> int:
    return _lerp([(0, -200), (300, -50), (600, 80), (900, 220), (1100, 340)], raw)


def curve_p06(raw: int) -> int:
    return _lerp([(20, -260), (200, -140), (450, 0), (700, 140), (950, 250)], raw)


def curve_p07(raw: int) -> int:
    return _lerp([(0, -310), (150, -220), (400, -40), (750, 150), (1000, 290)], raw)


def curve_p08(raw: int) -> int:
    return _lerp([(10, -270), (210, -120), (530, 15), (810, 175), (1020, 275)], raw)


CURVES = {
    "P01": curve_p01,
    "P02": curve_p02,
    "P03": curve_p03,
    "P04": curve_p04,
    "P05": curve_p05,
    "P06": curve_p06,
    "P07": curve_p07,
    "P08": curve_p08,
}


def correct(probe_id: str, raw: int) -> int:
    fn: Callable[[int], int] = CURVES[probe_id]
    return fn(raw)


def batch(probe_id: str, raws: List[int]) -> List[int]:
    return [correct(probe_id, raw) for raw in raws]
