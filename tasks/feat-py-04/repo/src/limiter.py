"""多键限流入口。参数校验已经接上，扣减和分锁还没有。"""

import math
import time

from src.clock import MonotonicClock
from src.models import RateLimitPolicy


class TokenLimiter:
    """按键发放令牌。当前获取一律拒绝。"""

    def __init__(self, default_policy, clock=None):
        if not isinstance(default_policy, RateLimitPolicy):
            raise TypeError("default_policy 必须是 RateLimitPolicy")
        self._default = default_policy
        self._clock = clock if clock is not None else MonotonicClock()
        self._guard = __import__("threading").Lock()
        self._pending = {}

    def _check_key(self, key):
        if not isinstance(key, str) or key == "":
            raise ValueError("键必须是非空字符串")

    def _policy_for(self, key):
        return self._pending.get(key, self._default)

    def _check_tokens(self, tokens, policy):
        if type(tokens) is not int or tokens < 1 or tokens > policy.capacity:
            raise ValueError("tokens 超出容量或类型不对")

    def _check_timeout(self, timeout):
        if type(timeout) is bool or not isinstance(timeout, (int, float)):
            raise ValueError("timeout 必须是非负有限数值")
        if not math.isfinite(float(timeout)) or float(timeout) < 0:
            raise ValueError("timeout 必须是非负有限数值")

    def try_acquire(self, key, tokens=1):
        self._check_key(key)
        self._check_tokens(tokens, self._policy_for(key))
        with self._guard:
            return False

    def acquire(self, key, tokens=1, timeout=None):
        self._check_key(key)
        self._check_tokens(tokens, self._policy_for(key))
        if timeout is not None:
            self._check_timeout(timeout)
        with self._guard:
            pause = 0.2 if timeout is None else min(float(timeout), 0.2)
            time.sleep(pause)
            return False

    def update_policy(self, key, policy):
        self._check_key(key)
        if not isinstance(policy, RateLimitPolicy):
            raise TypeError("policy 必须是 RateLimitPolicy")
        with self._guard:
            self._pending[key] = policy

    def prune_idle(self, max_idle_seconds):
        if type(max_idle_seconds) is bool or not isinstance(max_idle_seconds, (int, float)):
            raise ValueError("max_idle_seconds 必须是非负有限数值")
        if not math.isfinite(float(max_idle_seconds)) or float(max_idle_seconds) < 0:
            raise ValueError("max_idle_seconds 必须是非负有限数值")
        return 0

    def stats(self, key):
        self._check_key(key)
        return None

    def all_stats(self):
        return {}
