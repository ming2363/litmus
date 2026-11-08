"""引航委托"""


class PilotOrder(object):
    """引航委托"""

    def __init__(self, order_no, minutes, minimum_min, side):
        self.order_no = order_no
        self.minutes = minutes
        self.minimum_min = minimum_min
        self.side = side

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.order_no, str) or not (2 <= len(self.order_no) <= 16):
            errors.append("order_no")
        elif not self.order_no.replace("-", "").isalnum():
            errors.append("order_no")
        if isinstance(self.minutes, bool) or not isinstance(self.minutes, int):
            errors.append("minutes")
        elif self.minutes < 0 or self.minutes > 600:
            errors.append("minutes")
        if isinstance(self.minimum_min, bool) or not isinstance(self.minimum_min, int):
            errors.append("minimum_min")
        elif self.minimum_min < 30 or self.minimum_min > 180:
            errors.append("minimum_min")
        if self.side not in ("port", "starboard", "either"):
            errors.append("side")
        return errors

    def to_dict(self):
        return {"order_no": self.order_no, "minutes": self.minutes, "minimum_min": self.minimum_min, "side": self.side}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["order_no"], data["minutes"], data["minimum_min"], data["side"])

    def summary(self):
        return "PilotOrder:" + str(self.order_no)

    def billable_minutes(self):
        """不足起步分钟按起步计。"""
        if self.minutes < self.minimum_min:
            return self.minimum_min
        return self.minutes

