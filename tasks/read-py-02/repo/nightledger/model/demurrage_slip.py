"""滞期草稿"""


class DemurrageSlip(object):
    """滞期草稿"""

    def __init__(self, slip_no, minutes, cap_min, reason):
        self.slip_no = slip_no
        self.minutes = minutes
        self.cap_min = cap_min
        self.reason = reason

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.slip_no, str) or not (2 <= len(self.slip_no) <= 16):
            errors.append("slip_no")
        elif not self.slip_no.replace("-", "").isalnum():
            errors.append("slip_no")
        if isinstance(self.minutes, bool) or not isinstance(self.minutes, int):
            errors.append("minutes")
        elif self.minutes < 0 or self.minutes > 20000:
            errors.append("minutes")
        if isinstance(self.cap_min, bool) or not isinstance(self.cap_min, int):
            errors.append("cap_min")
        elif self.cap_min < 1 or self.cap_min > 20000:
            errors.append("cap_min")
        if not isinstance(self.reason, str) or not self.reason.strip():
            errors.append("reason")
        elif len(self.reason.strip()) > 40:
            errors.append("reason")
        return errors

    def to_dict(self):
        return {"slip_no": self.slip_no, "minutes": self.minutes, "cap_min": self.cap_min, "reason": self.reason}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["slip_no"], data["minutes"], data["cap_min"], data["reason"])

    def summary(self):
        return "DemurrageSlip:" + str(self.slip_no)

    def capped_minutes(self):
        """滞期分钟不超过封顶。"""
        if self.minutes > self.cap_min:
            return self.cap_min
        return self.minutes

