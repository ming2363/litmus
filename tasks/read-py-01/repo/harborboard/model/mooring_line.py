"""系缆记录"""


class MooringLine(object):
    """系缆记录"""

    def __init__(self, berth, count, minimum, material):
        self.berth = berth
        self.count = count
        self.minimum = minimum
        self.material = material

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.berth, str) or not (2 <= len(self.berth) <= 16):
            errors.append("berth")
        elif not self.berth.replace("-", "").isalnum():
            errors.append("berth")
        if isinstance(self.count, bool) or not isinstance(self.count, int):
            errors.append("count")
        elif self.count < 0 or self.count > 20:
            errors.append("count")
        if isinstance(self.minimum, bool) or not isinstance(self.minimum, int):
            errors.append("minimum")
        elif self.minimum < 2 or self.minimum > 12:
            errors.append("minimum")
        if self.material not in ("wire", "rope", "mixed"):
            errors.append("material")
        return errors

    def to_dict(self):
        return {"berth": self.berth, "count": self.count, "minimum": self.minimum, "material": self.material}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["berth"], data["count"], data["minimum"], data["material"])

    def summary(self):
        return "MooringLine:" + str(self.berth)

    def enough(self):
        """缆绳根数达到最低要求。"""
        return self.count >= self.minimum

