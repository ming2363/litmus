"""时钟。令牌桶只通过 now() 看时间。"""

import time


class Clock:
    """时钟抽象。"""

    def now(self):
        raise NotImplementedError


class MonotonicClock(Clock):
    """单调时钟。"""

    def now(self):
        return float(time.monotonic())


class ManualClock(Clock):
    """测试用时钟，不会自己走动。"""

    def __init__(self, start=0.0):
        self._now = float(start)

    def now(self):
        return self._now

    def advance(self, delta):
        if type(delta) is bool or not isinstance(delta, (int, float)) or delta < 0:
            raise ValueError("advance 只接受非负数值")
        self._now += float(delta)

    def set(self, value):
        if type(value) is bool or not isinstance(value, (int, float)):
            raise ValueError("set 只接受有限数值")
        number = float(value)
        if number != number or number in (float("inf"), float("-inf")):
            raise ValueError("set 只接受有限数值")
        self._now = number
