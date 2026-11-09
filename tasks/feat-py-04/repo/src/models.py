"""策略和统计快照。"""

import math


class RateLimitPolicy:
    """一把桶的容量、补充速度和闲置冻结。"""

    def __init__(self, capacity, rate, freeze_after=None, burst=None):
        if type(capacity) is not int or capacity < 1:
            raise ValueError("capacity 必须是正整数")
        if type(rate) is bool or not isinstance(rate, (int, float)):
            raise ValueError("rate 必须是非负有限数值")
        rate_value = float(rate)
        if not math.isfinite(rate_value) or rate_value < 0:
            raise ValueError("rate 必须是非负有限数值")
        if burst is not None and (type(burst) is not int or burst != capacity):
            raise ValueError("burst 必须等于 capacity")
        if freeze_after is not None:
            if type(freeze_after) is bool or not isinstance(freeze_after, (int, float)):
                raise ValueError("freeze_after 必须是非负有限数值或 None")
            freeze_value = float(freeze_after)
            if not math.isfinite(freeze_value) or freeze_value < 0:
                raise ValueError("freeze_after 必须是非负有限数值或 None")
        else:
            freeze_value = None
        self.capacity = capacity
        self.rate = rate_value
        self.freeze_after = freeze_value
        self.burst = capacity


class BucketStats:
    """一次读取看到的桶状态。"""

    def __init__(
        self,
        tokens,
        capacity,
        rate,
        freeze_after,
        allowed_requests,
        allowed_tokens,
        rejected_requests,
        last_active,
        waiters,
    ):
        self.tokens = tokens
        self.capacity = capacity
        self.rate = rate
        self.freeze_after = freeze_after
        self.allowed_requests = allowed_requests
        self.allowed_tokens = allowed_tokens
        self.rejected_requests = rejected_requests
        self.last_active = last_active
        self.waiters = waiters
