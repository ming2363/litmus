"""可注入的单调时钟与手动测试时钟。"""

import threading
import time


class Clock:
    """时钟基类，返回单调递增的秒数。"""

    def now(self) -> float:
        raise NotImplementedError


class MonotonicClock(Clock):
    """基于系统单调时钟的实现。"""

    def now(self) -> float:
        return time.monotonic()


class ManualClock(Clock):
    """线程安全的手动推进时钟，便于确定性测试。"""

    def __init__(self, initial: float = 0.0) -> None:
        self._lock = threading.Lock()
        self._now = float(initial)

    def now(self) -> float:
        with self._lock:
            return self._now

    def advance(self, seconds: float) -> float:
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("推进时间必须为非负数: {!r}".format(seconds))
        with self._lock:
            self._now += float(seconds)
            return self._now
