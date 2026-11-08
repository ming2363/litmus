"""平面近似就够用的距离，坐标单位是「毫度」。"""

import math as _math


def to_rad(milli_deg):
    return (milli_deg / 1000.0) * _math.pi / 180.0


def haversine_m(lat1, lon1, lat2, lon2):
    """返回两点间米数，输入是毫度整数。"""
    earth = 6371000.0
    p1 = to_rad(lat1)
    p2 = to_rad(lat2)
    dp = to_rad(lat2 - lat1)
    dl = to_rad(lon2 - lon1)
    a = _math.sin(dp / 2) ** 2 + _math.cos(p1) * _math.cos(p2) * _math.sin(dl / 2) ** 2
    return 2 * earth * _math.asin(min(1.0, _math.sqrt(a)))


def inside_box(lat, lon, south, west, north, east):
    """闭区间包围盒。跨越 180 度经线时不支持。"""
    if west > east or south > north:
        raise ValueError("box")
    return south <= lat <= north and west <= lon <= east


def nearest(origin, points):
    """points 为 (name, lat, lon)。返回最近的 name 与米数。"""
    if not points:
        raise ValueError("points")
    best_name = None
    best_dist = None
    for name, lat, lon in points:
        dist = haversine_m(origin[0], origin[1], lat, lon)
        if best_dist is None or dist < best_dist:
            best_name = name
            best_dist = dist
    return best_name, best_dist
