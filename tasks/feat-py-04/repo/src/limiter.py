"""多键令牌桶限流器（起始原型未实现并发安全与阻塞等待等高级能力）。"""

from typing import Dict, Optional

from src.bucket import TokenBucket
from src.clock import Clock, MonotonicClock
from src.models import BucketStats, RateLimitPolicy


class TokenLimiter:
    """多键令牌桶限流器。"""

    def __init__(
        self,
        default_policy: RateLimitPolicy,
        clock: Optional[Clock] = None,
    ) -> None:
        if not isinstance(default_policy, RateLimitPolicy):
            raise ValueError("default_policy 必须是 RateLimitPolicy 实例")
        self._default_policy = default_policy
        self._clock = clock if clock is not None else MonotonicClock()
        self._buckets: Dict[str, TokenBucket] = {}

    def _get_or_create(self, key: str) -> TokenBucket:
        if not isinstance(key, str) or not key:
            raise ValueError("key 必须是非空字符串")
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = TokenBucket(key, self._default_policy, self._clock.now())
            self._buckets[key] = bucket
        return bucket

    def try_acquire(self, key: str, tokens: int = 1) -> bool:
        if isinstance(tokens, bool) or not isinstance(tokens, int) or tokens <= 0:
            raise ValueError("tokens 必须是正整数")
        bucket = self._get_or_create(key)
        # 原型代码未加锁，读写检查与更新存在竞态窗口
        bucket.refill(self._clock.now())
        if bucket.tokens >= tokens:
            bucket.last_active = self._clock.now()
            bucket.tokens -= tokens
            bucket.allowed_requests += 1
            bucket.allowed_tokens += tokens
            return True
        bucket.last_active = self._clock.now()
        bucket.rejected_requests += 1
        return False

    def acquire(
        self,
        key: str,
        tokens: int = 1,
        timeout: Optional[float] = None,
    ) -> bool:
        raise NotImplementedError("acquire 尚未实现")

    def update_policy(self, key: str, policy: RateLimitPolicy) -> None:
        raise NotImplementedError("update_policy 尚未实现")

    def prune_idle(self, max_idle_seconds: float) -> int:
        raise NotImplementedError("prune_idle 尚未实现")

    def stats(self, key: str) -> Optional[BucketStats]:
        bucket = self._buckets.get(key)
        if bucket is None:
            return None
        return bucket.snapshot(self._clock.now())

    def all_stats(self) -> Dict[str, BucketStats]:
        now = self._clock.now()
        return {k: b.snapshot(now) for k, b in self._buckets.items()}
