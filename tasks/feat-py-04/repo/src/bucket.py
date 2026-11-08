"""单键令牌桶状态（起始原型缺少线程同步与精度控制）。"""

from src.models import BucketStats, RateLimitPolicy


class TokenBucket:
    """单键令牌桶。"""

    def __init__(self, key: str, policy: RateLimitPolicy, now: float) -> None:
        self.key = key
        self.policy = policy
        self.tokens = float(policy.capacity)
        self.last_refill = float(now)
        self.last_active = float(now)
        self.allowed_requests = 0
        self.allowed_tokens = 0
        self.rejected_requests = 0

    def refill(self, now: float) -> None:
        elapsed = max(0.0, float(now) - self.last_refill)
        if elapsed > 0.0 and self.policy.rate > 0.0:
            self.tokens = min(self.policy.capacity, self.tokens + elapsed * self.policy.rate)
        self.last_refill = float(now)

    def snapshot(self, now: float) -> BucketStats:
        self.refill(now)
        return BucketStats(
            key=self.key,
            tokens=self.tokens,
            capacity=self.policy.capacity,
            rate=self.policy.rate,
            allowed_requests=self.allowed_requests,
            allowed_tokens=self.allowed_tokens,
            rejected_requests=self.rejected_requests,
        )
