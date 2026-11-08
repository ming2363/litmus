"""码头常用单位换算，全部整数毫单位。"""


def tonnes_to_kg(milli_tonnes):
    """毫吨到千克。1 吨 = 1000 千克，输入是千分之一吨。"""
    if milli_tonnes < 0:
        raise ValueError("tonnes")
    return milli_tonnes


def cm_to_mm(cm):
    if cm < 0:
        raise ValueError("cm")
    return cm * 10


def knots_to_mps_milli(knots_milli):
    """毫节换成毫米每秒。1 节 = 0.514444 米/秒，这里取 514。"""
    if knots_milli < 0:
        raise ValueError("knots")
    return knots_milli * 514


def minutes_to_millis_checked(minutes, ceiling):
    """分钟转毫秒，用长整数路径，超过 ceiling 分钟就拒绝。"""
    if minutes < 0 or minutes > ceiling:
        raise ValueError("minutes")
    return minutes * 60 * 1000


def clamp_unit(value, low, high):
    if low > high:
        raise ValueError("range")
    return min(max(value, low), high)
