"""潮汐窗口"""


class TideWindow(object):
    """潮汐窗口"""

    def __init__(self, code, start_min, end_min, height_cm):
        self.code = code
        self.start_min = start_min
        self.end_min = end_min
        self.height_cm = height_cm

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.code, str) or not (2 <= len(self.code) <= 16):
            errors.append("code")
        elif not self.code.replace("-", "").isalnum():
            errors.append("code")
        if isinstance(self.start_min, bool) or not isinstance(self.start_min, int):
            errors.append("start_min")
        elif self.start_min < 0 or self.start_min > 1440:
            errors.append("start_min")
        if isinstance(self.end_min, bool) or not isinstance(self.end_min, int):
            errors.append("end_min")
        elif self.end_min < 0 or self.end_min > 2880:
            errors.append("end_min")
        if isinstance(self.height_cm, bool) or not isinstance(self.height_cm, int):
            errors.append("height_cm")
        elif self.height_cm < 0 or self.height_cm > 900:
            errors.append("height_cm")
        return errors

    def to_dict(self):
        return {"code": self.code, "start_min": self.start_min, "end_min": self.end_min, "height_cm": self.height_cm}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["code"], data["start_min"], data["end_min"], data["height_cm"])

    def summary(self):
        return "TideWindow:" + str(self.code)

    def contains_minute(self, minute):
        """分钟落在半开窗口内。"""
        return self.start_min <= minute < self.end_min

