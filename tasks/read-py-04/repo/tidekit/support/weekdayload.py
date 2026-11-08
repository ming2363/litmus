"""按星期汇总工作量。星期一是 0。"""

import datetime as _dt


def by_weekday(pairs):
    """pairs 为 (date, amount)。返回长度 7 的列表。"""
    loads = [0 for _ in range(7)]
    for day, amount in pairs:
        if not isinstance(day, _dt.date):
            raise TypeError("date")
        loads[day.weekday()] += amount
    return loads


def peak_weekday(pairs):
    loads = by_weekday(pairs)
    best = 0
    for idx, value in enumerate(loads):
        if value > loads[best]:
            best = idx
    return best, loads[best]


def share_bps(pairs):
    """各星期占比，万分比，余数补给最大的一天。"""
    loads = by_weekday(pairs)
    total = sum(loads)
    if total == 0:
        return [0 for _ in loads]
    raw = [value * 10000 for value in loads]
    shares = [item // total for item in raw]
    remain = 10000 - sum(shares)
    order = sorted(range(7), key=lambda i: (-(raw[i] % total), i))
    for idx in range(remain):
        shares[order[idx]] += 1
    return shares
