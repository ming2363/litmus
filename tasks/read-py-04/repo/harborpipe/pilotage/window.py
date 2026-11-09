"""引航窗口：潮高、富余水深、白昼和潮流。时间是当天的分钟，高度是厘米。"""

from typing import List, Optional, Sequence, Tuple


TidePoint = Tuple[int, int]


class PilotageError(ValueError):
    """引航计算的输入不合法。"""


def _check_series(series: Sequence[TidePoint]) -> List[TidePoint]:
    if len(series) < 2:
        raise PilotageError("潮汐至少要两个点")
    ordered = list(series)
    for index, (minute, height) in enumerate(ordered):
        if type(minute) is not int or type(height) is not int:
            raise PilotageError("潮汐点必须是整数")
        if index and minute <= ordered[index - 1][0]:
            raise PilotageError("潮汐时间必须递增")
    return ordered


def tide_height(series: Sequence[TidePoint], minute: int) -> int:
    """线性插值。询问时间落在样本之外时，沿用端点高度，不外推斜率。"""
    ordered = _check_series(series)
    if minute <= ordered[0][0]:
        return ordered[0][1]
    if minute >= ordered[-1][0]:
        return ordered[-1][1]
    for index in range(1, len(ordered)):
        left_m, left_h = ordered[index - 1]
        right_m, right_h = ordered[index]
        if left_m <= minute <= right_m:
            span = right_m - left_m
            return left_h + (right_h - left_h) * (minute - left_m) // span
    raise PilotageError("潮汐插值失败")


def squat_cm(block: int, speed_kn_x10: int, depth_cm: int, draft_cm: int) -> int:
    """方形系数千分比、航速十分之一节。水深不足吃水时直接拒绝。"""
    if not 500 <= block <= 900:
        raise PilotageError("方形系数超出范围")
    if speed_kn_x10 < 0 or depth_cm <= draft_cm or draft_cm <= 0:
        raise PilotageError("下沉量参数不合法")
    # 经验式：Cb * V^2 * 吃水 / (水深 - 吃水) / 常数。结果用厘米。
    speed2 = speed_kn_x10 * speed_kn_x10
    return block * speed2 * draft_cm // ((depth_cm - draft_cm) * 20000)


def under_keel(tide_cm: int, chart_depth_cm: int, draft_cm: int, squat: int, allowance_cm: int) -> int:
    """富余水深 = 潮高 + 海图水深 - 吃水 - 下沉 - 政策余量。"""
    return tide_cm + chart_depth_cm - draft_cm - squat - allowance_cm


def daylight(sunrise: int, sunset: int, need: int) -> Optional[Tuple[int, int]]:
    """白昼可用段。需要的分钟若长于白昼，返回空。"""
    if not 0 <= sunrise < sunset <= 24 * 60:
        raise PilotageError("日出日落不合法")
    if need < 0:
        raise PilotageError("所需时长不能为负")
    if sunset - sunrise < need:
        return None
    return (sunrise, sunset)


def current_limit(draft_cm: int) -> int:
    """返回允许的最大流速，单位是厘米每秒。吃水越深，允许的流越慢。"""
    if draft_cm <= 800:
        return 180
    if draft_cm <= 1100:
        return 140
    if draft_cm <= 1400:
        return 100
    return 70


def clip_interval(start: int, end: int, left: int, right: int) -> Optional[Tuple[int, int]]:
    lo = start if start > left else left
    hi = end if end < right else right
    if lo >= hi:
        return None
    return (lo, hi)


def tide_windows(
    series: Sequence[TidePoint],
    chart_depth_cm: int,
    draft_cm: int,
    speed_kn_x10: int,
    block: int,
    allowance_cm: int,
    step: int = 10,
) -> List[Tuple[int, int]]:
    """按固定步长扫描，富余水深不小于 0 的连续分钟收成半开窗口。"""
    ordered = _check_series(series)
    if step <= 0:
        raise PilotageError("步长必须为正")
    open_at: Optional[int] = None
    windows: List[Tuple[int, int]] = []
    minute = ordered[0][0]
    last = ordered[-1][0]
    while minute <= last:
        height = tide_height(ordered, minute)
        sink = squat_cm(block, speed_kn_x10, chart_depth_cm + height, draft_cm)
        spare = under_keel(height, chart_depth_cm, draft_cm, sink, allowance_cm)
        if spare >= 0 and open_at is None:
            open_at = minute
        elif spare < 0 and open_at is not None:
            windows.append((open_at, minute))
            open_at = None
        minute += step
    if open_at is not None:
        windows.append((open_at, last + step))
    return windows


def current_windows(samples: Sequence[Tuple[int, int]], limit_cm_s: int) -> List[Tuple[int, int]]:
    """流速样本是 (分钟, 厘米每秒)。不超过限值的连续段收成窗口。"""
    if not samples:
        return []
    windows: List[Tuple[int, int]] = []
    open_at: Optional[int] = None
    previous = samples[0][0]
    for minute, speed in samples:
        if type(minute) is not int or type(speed) is not int or speed < 0:
            raise PilotageError("流速样本不合法")
        if minute < previous:
            raise PilotageError("流速时间倒退")
        previous = minute
        if speed <= limit_cm_s and open_at is None:
            open_at = minute
        elif speed > limit_cm_s and open_at is not None:
            windows.append((open_at, minute))
            open_at = None
    if open_at is not None:
        windows.append((open_at, samples[-1][0] + 1))
    return windows


def intersect(left: Sequence[Tuple[int, int]], right: Sequence[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """两组半开窗口的交集。"""
    result: List[Tuple[int, int]] = []
    i = 0
    j = 0
    a = list(left)
    b = list(right)
    while i < len(a) and j < len(b):
        lo = a[i][0] if a[i][0] > b[j][0] else b[j][0]
        hi = a[i][1] if a[i][1] < b[j][1] else b[j][1]
        if lo < hi:
            result.append((lo, hi))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return result


def long_enough(windows: Sequence[Tuple[int, int]], need: int) -> List[Tuple[int, int]]:
    return [item for item in windows if item[1] - item[0] >= need]


def boarding_side(wind_from: str, flood: bool) -> str:
    """风向用八方位。涨潮时船首迎流，横风把引航梯放到下风舷。"""
    table = {
        "N": "S",
        "NE": "SW",
        "E": "W",
        "SE": "NW",
        "S": "N",
        "SW": "NE",
        "W": "E",
        "NW": "SE",
    }
    if wind_from not in table:
        raise PilotageError("风向不存在")
    if wind_from in ("N", "S"):
        return "P" if flood else "S"
    return "S" if wind_from in ("E", "NE", "SE") else "P"


def pilot_windows(
    tides: Sequence[TidePoint],
    currents: Sequence[Tuple[int, int]],
    chart_depth_cm: int,
    draft_cm: int,
    speed_kn_x10: int,
    block: int,
    allowance_cm: int,
    sunrise: int,
    sunset: int,
    transit_minutes: int,
) -> List[Tuple[int, int]]:
    """潮水、潮流、白昼三者都满足，并且窗口能走完 transit_minutes 的段。"""
    by_tide = tide_windows(tides, chart_depth_cm, draft_cm, speed_kn_x10, block, allowance_cm)
    by_current = current_windows(currents, current_limit(draft_cm))
    both = intersect(by_tide, by_current)
    light = daylight(sunrise, sunset, transit_minutes)
    if light is None:
        return []
    clipped: List[Tuple[int, int]] = []
    for start, end in both:
        piece = clip_interval(start, end, light[0], light[1])
        if piece is not None:
            clipped.append(piece)
    return long_enough(clipped, transit_minutes)


def first_boarding(windows: Sequence[Tuple[int, int]]) -> Optional[int]:
    if not windows:
        return None
    return min(item[0] for item in windows)
