"""停泊费试算，看板路由不调用这里。"""


def stay_fen(hours, night_hours, length_m):
    """小时费加夜间加成，再按船长分档封顶。"""
    if hours < 0 or night_hours < 0 or night_hours > hours:
        raise ValueError("hours")
    if length_m <= 0:
        raise ValueError("length")
    base = hours * 1800
    base += night_hours * 700
    if length_m > 180:
        cap = 250000
    elif length_m > 120:
        cap = 160000
    else:
        cap = 90000
    if base > cap:
        return cap
    return base


def explain(hours, night_hours, length_m):
    """给出试算说明。"""
    amount = stay_fen(hours, night_hours, length_m)
    return {"fen": amount, "hours": hours, "night_hours": night_hours}
