"""令牌桶限流策略与统计模型。"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class RateLimitPolicy:
    """限流策略：rate 为每秒补充令牌数，capacity 为桶最大容量。"""

    rate: float
    capacity: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.rate, bool)
            or not isinstance(self.rate, (int, float))
            or not math.isfinite(self.rate)
            or self.rate < 0.0
        ):
            raise ValueError("rate 必须为有限非负数: {!r}".format(self.rate))
        if (
            isinstance(self.capacity, bool)
            or not isinstance(self.capacity, (int, float))
            or not math.isfinite(self.capacity)
            or self.capacity <= 0.0
        ):
            raise ValueError("capacity 必须为有限正数: {!r}".format(self.capacity))
        object.__setattr__(self, "rate", float(self.rate))
        object.__setattr__(self, "capacity", float(self.capacity))


@dataclass(frozen=True)
class BucketStats:
    """单个键的限流桶统计快照。"""

    key: str
    tokens: float
    capacity: float
    rate: float
    allowed_requests: int
    allowed_tokens: int
    rejected_requests: int
