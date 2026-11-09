"""旧闸口草稿。

整座闸口共用一把锁，令牌一直按 rate 补到 capacity，没有闲置冻结。
新规则不要沿用这份行为。TokenLimiter 也没有调用这里。
"""

import threading
import time

from src.clock import MonotonicClock
from src.models import RateLimitPolicy


class LegacyGate:
    """单键的经典令牌桶。"""

    def __init__(self, policy, clock=None):
        if not isinstance(policy, RateLimitPolicy):
            raise TypeError("policy 必须是 RateLimitPolicy")
        self.policy = policy
        self.clock = clock if clock is not None else MonotonicClock()
        self.tokens = float(policy.capacity)
        self.last_refill = self.clock.now()
        self._lock = threading.Lock()

    def _refill(self, now):
        elapsed = now - self.last_refill
        if elapsed < 0:
            elapsed = 0.0
        self.tokens = min(float(self.policy.capacity), self.tokens + elapsed * self.policy.rate)
        self.last_refill = now

    def try_take(self, tokens=1):
        with self._lock:
            now = self.clock.now()
            self._refill(now)
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def take(self, tokens=1, timeout=1.0):
        deadline = time.monotonic() + float(timeout)
        while True:
            if self.try_take(tokens):
                return True
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.01)
