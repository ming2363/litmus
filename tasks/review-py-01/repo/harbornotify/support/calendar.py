"""2026 年业务日历。节假日写死，避免依赖系统时区数据库。"""

import datetime as _dt


HOLIDAYS_2026 = {
    _dt.date(2026, 1, 1),
    _dt.date(2026, 2, 16),
    _dt.date(2026, 2, 17),
    _dt.date(2026, 2, 18),
    _dt.date(2026, 2, 19),
    _dt.date(2026, 4, 6),
    _dt.date(2026, 5, 1),
    _dt.date(2026, 6, 19),
    _dt.date(2026, 10, 1),
    _dt.date(2026, 10, 2),
    _dt.date(2026, 10, 5),
}

EXTRA_WORKDAYS_2026 = {
    _dt.date(2026, 2, 14),
    _dt.date(2026, 10, 10),
}


def parse_date(text):
    """只接受 YYYY-MM-DD。"""
    if not isinstance(text, str) or len(text) != 10:
        raise ValueError(text)
    try:
        return _dt.datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(text) from exc


def is_business_day(day):
    """周末默认休息，调休上班日除外；法定假日优先休息。"""
    if day in HOLIDAYS_2026:
        return False
    if day in EXTRA_WORKDAYS_2026:
        return True
    return day.weekday() < 5


def add_business_days(day, count):
    """向前（正）或向后（负）移动 count 个业务日，不含起始日。"""
    if count == 0:
        return day
    step = 1 if count > 0 else -1
    left = abs(count)
    cursor = day
    while left:
        cursor += _dt.timedelta(days=step)
        if is_business_day(cursor):
            left -= 1
    return cursor


def business_span(start, end):
    """闭区间内的业务日数量。起大于止时返回 0。"""
    if end < start:
        return 0
    cursor = start
    total = 0
    while cursor <= end:
        if is_business_day(cursor):
            total += 1
        cursor += _dt.timedelta(days=1)
    return total


def month_bounds(year, month):
    """返回该月第一天和最后一天。"""
    if month < 1 or month > 12:
        raise ValueError(month)
    first = _dt.date(year, month, 1)
    if month == 12:
        nxt = _dt.date(year + 1, 1, 1)
    else:
        nxt = _dt.date(year, month + 1, 1)
    return first, nxt - _dt.timedelta(days=1)
