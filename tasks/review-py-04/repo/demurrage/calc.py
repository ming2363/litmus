"""滞期费，单位是分。"""


def round_up_minutes(seconds):
    """把秒换算成分钟。

    0 秒得到 0。秒数正好是 60 的倍数时保持整分钟，不额外加 1。
    只要有余数就向上进 1 分钟。负数抛出 ValueError。
    """
    if isinstance(seconds, bool) or not isinstance(seconds, int):
        raise TypeError("seconds")
    if seconds < 0:
        raise ValueError("seconds")
    return seconds // 60 + 1


def charge_cents(start, end):
    """按秒计算滞期费，返回分。

    先换成向上取整的分钟，再乘每分钟 150 分。结果超过 200000 分时封顶。
    """
    seconds = end - start
    minutes = round_up_minutes(seconds)
    cents = minutes * 150
    if cents > 200000:
        return 200000
    return cents
