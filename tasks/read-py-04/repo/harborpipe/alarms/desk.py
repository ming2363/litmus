"""冷箱报警。每种码看的采样窗口和阈值都不一样。"""

from typing import List, Sequence, Tuple

Sample = Tuple[int, int]  # 分钟, 十分之一摄氏度


def _window(samples: Sequence[Sample], start: int, end: int) -> List[Sample]:
    return [item for item in samples if start <= item[0] < end]


def high_temp(samples: Sequence[Sample], limit: int, hold_minutes: int) -> bool:
    """连续高于上限达到 hold_minutes 才算。"""
    if hold_minutes <= 0:
        raise ValueError("持续时间不合法")
    run_start = None
    previous = None
    for minute, value in samples:
        if previous is not None and minute < previous:
            raise ValueError("采样时间倒退")
        previous = minute
        if value > limit:
            if run_start is None:
                run_start = minute
            if minute - run_start >= hold_minutes:
                return True
        else:
            run_start = None
    return False


def low_temp(samples: Sequence[Sample], limit: int, hold_minutes: int) -> bool:
    run_start = None
    for minute, value in samples:
        if value < limit:
            if run_start is None:
                run_start = minute
            if minute - run_start >= hold_minutes:
                return True
        else:
            run_start = None
    return False


def spike(samples: Sequence[Sample], jump: int) -> bool:
    """相邻两点的跳变。"""
    if jump <= 0:
        raise ValueError("跳变阈值不合法")
    previous = None
    for minute, value in samples:
        if previous is not None and abs(value - previous) >= jump:
            return True
        previous = value
    return False


def flatline(samples: Sequence[Sample], minutes: int) -> bool:
    """探头长时间完全不变，视为失效。"""
    if len(samples) < 2 or minutes <= 0:
        return False
    anchor = samples[0]
    for minute, value in samples[1:]:
        if value != anchor[1]:
            anchor = (minute, value)
            continue
        if minute - anchor[0] >= minutes:
            return True
    return False


def rate_of_rise(samples: Sequence[Sample], per_hour: int) -> bool:
    """任意一小时窗口内升温超过 per_hour。"""
    for index, (minute, value) in enumerate(samples):
        for later_minute, later_value in samples[index + 1 :]:
            elapsed = later_minute - minute
            if elapsed <= 0:
                continue
            if elapsed > 60:
                break
            if (later_value - value) * 60 >= per_hour * elapsed:
                return True
    return False


def missing_gap(samples: Sequence[Sample], gap: int) -> bool:
    previous = None
    for minute, _value in samples:
        if previous is not None and minute - previous > gap:
            return True
        previous = minute
    return False


def mean_above(samples: Sequence[Sample], start: int, end: int, limit: int) -> bool:
    rows = _window(samples, start, end)
    if not rows:
        return False
    total = sum(value for _minute, value in rows)
    return total > limit * len(rows)


def count_crossings(samples: Sequence[Sample], line: int) -> int:
    crossings = 0
    previous = None
    for _minute, value in samples:
        if previous is not None and ((previous <= line < value) or (value <= line < previous)):
            crossings += 1
        previous = value
    return crossings


def recovery_minute(samples: Sequence[Sample], low: int, high: int) -> int:
    """第一次回到闭区间的分钟。没有则抛错。"""
    for minute, value in samples:
        if low <= value <= high:
            return minute
    raise LookupError("没有回到区间")

def policy_meat(samples: Sequence[Sample], setpoint: int) -> bool:
    return high_temp(samples, setpoint + 20, 30) or spike(samples, 25)

def policy_fish(samples: Sequence[Sample], setpoint: int) -> bool:
    return low_temp(samples, setpoint - 30, 20) or flatline(samples, 90)

def policy_banana(samples: Sequence[Sample], setpoint: int) -> bool:
    return high_temp(samples, setpoint + 10, 15) or rate_of_rise(samples, 12)

def policy_drug(samples: Sequence[Sample], setpoint: int) -> bool:
    return spike(samples, 8) or missing_gap(samples, 20) or high_temp(samples, setpoint + 5, 10)

def policy_cocoa(samples: Sequence[Sample], setpoint: int) -> bool:
    return high_temp(samples, setpoint + 15, 40) and not flatline(samples, 30)

def policy_ice(samples: Sequence[Sample], setpoint: int) -> bool:
    return low_temp(samples, setpoint - 10, 15) or high_temp(samples, setpoint + 8, 10)

def policy_plasma(samples: Sequence[Sample], setpoint: int) -> bool:
    return missing_gap(samples, 10) or spike(samples, 4) or high_temp(samples, setpoint + 3, 5)

def policy_vaccine(samples: Sequence[Sample], setpoint: int) -> bool:
    return high_temp(samples, setpoint + 2, 5) or low_temp(samples, setpoint - 2, 5)

def policy_flower(samples: Sequence[Sample], setpoint: int) -> bool:
    return rate_of_rise(samples, 20) or high_temp(samples, setpoint + 25, 60)

def policy_cheese(samples: Sequence[Sample], setpoint: int) -> bool:
    return count_crossings(samples, setpoint) >= 4 or flatline(samples, 120)


POLICIES = {
    "冻肉": policy_meat,
    "冻鱼": policy_fish,
    "香蕉": policy_banana,
    "药品": policy_drug,
    "巧克力": policy_cocoa,
    "冰淇淋": policy_ice,
    "血浆": policy_plasma,
    "疫苗": policy_vaccine,
    "鲜花": policy_flower,
    "奶酪": policy_cheese,
}


def raised(cargo: str, samples: Sequence[Sample], setpoint: int) -> bool:
    fn = POLICIES.get(cargo)
    if fn is None:
        raise KeyError(cargo)
    return fn(samples, setpoint)
