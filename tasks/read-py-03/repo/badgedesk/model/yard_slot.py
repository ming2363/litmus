"""堆场箱位"""


class YardSlot(object):
    """堆场箱位"""

    def __init__(self, slot_no, length_m, status, tier):
        self.slot_no = slot_no
        self.length_m = length_m
        self.status = status
        self.tier = tier

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.slot_no, str) or not (2 <= len(self.slot_no) <= 16):
            errors.append("slot_no")
        elif not self.slot_no.replace("-", "").isalnum():
            errors.append("slot_no")
        if isinstance(self.length_m, bool) or not isinstance(self.length_m, int):
            errors.append("length_m")
        elif self.length_m < 3 or self.length_m > 20:
            errors.append("length_m")
        if self.status not in ("empty", "occupied", "locked"):
            errors.append("status")
        if isinstance(self.tier, bool) or not isinstance(self.tier, int):
            errors.append("tier")
        elif self.tier < 1 or self.tier > 6:
            errors.append("tier")
        return errors

    def to_dict(self):
        return {"slot_no": self.slot_no, "length_m": self.length_m, "status": self.status, "tier": self.tier}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["slot_no"], data["length_m"], data["status"], data["tier"])

    def summary(self):
        return "YardSlot:" + str(self.slot_no)

    def fits(self, length_m):
        """箱位长度够用且空闲。"""
        return self.status == "empty" and length_m <= self.length_m

