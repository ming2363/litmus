"""单键桶的草稿。补充方式与旧闸口相同，没有冻结。"""

from src.models import BucketStats


class TokenBucket:
    """保存一把桶的令牌和计数。并发由调用方加锁。"""

    def __init__(self, policy, now):
        self.policy = policy
        self.tokens = float(policy.capacity)
        self.last_refill = float(now)
        self.last_active = float(now)
        self.allowed_requests = 0
        self.allowed_tokens = 0
        self.rejected_requests = 0
        self.waiters = 0

    def refill(self, now):
        """按整段空闲时间补充，并封顶。"""
        elapsed = float(now) - self.last_refill
        if elapsed < 0:
            elapsed = 0.0
        self.tokens = min(
            float(self.policy.capacity),
            self.tokens + elapsed * float(self.policy.rate),
        )
        self.last_refill = float(now)

    def snapshot(self):
        return BucketStats(
            tokens=self.tokens,
            capacity=self.policy.capacity,
            rate=self.policy.rate,
            freeze_after=self.policy.freeze_after,
            allowed_requests=self.allowed_requests,
            allowed_tokens=self.allowed_tokens,
            rejected_requests=self.rejected_requests,
            last_active=self.last_active,
            waiters=self.waiters,
        )
