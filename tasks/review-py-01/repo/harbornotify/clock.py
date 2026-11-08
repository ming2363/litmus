"""通知上的班次标签。"""


def shift_label(minute):
    """0 到 1439 的分钟。"""
    if minute < 0 or minute >= 1440:
        raise ValueError("minute")
    if minute < 480:
        return "night"
    if minute < 960:
        return "day"
    return "evening"
