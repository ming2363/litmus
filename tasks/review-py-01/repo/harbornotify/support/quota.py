"""单线程配额账本，按主体累计，不做并发控制。"""


class QuotaBook(object):
    """记录某个周期内的已用量。"""

    def __init__(self, limits):
        self.limits = dict(limits)
        self.used = {key: 0 for key in self.limits}

    def remaining(self, key):
        if key not in self.limits:
            raise KeyError(key)
        return self.limits[key] - self.used[key]

    def try_take(self, key, amount):
        """够用才扣减。amount 必须为正。"""
        if amount <= 0:
            raise ValueError("amount")
        if self.remaining(key) < amount:
            return False
        self.used[key] += amount
        return True

    def refund(self, key, amount):
        """回冲，不能高于已用量。"""
        if amount <= 0 or amount > self.used.get(key, 0):
            raise ValueError("refund")
        self.used[key] -= amount

    def snapshot(self):
        return {
            key: {"limit": self.limits[key], "used": self.used[key]}
            for key in sorted(self.limits)
        }
