"""气象管制"""


class WeatherHold(object):
    """气象管制"""

    def __init__(self, notice_no, level, hours):
        self.notice_no = notice_no
        self.level = level
        self.hours = hours

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.notice_no, str) or not (2 <= len(self.notice_no) <= 16):
            errors.append("notice_no")
        elif not self.notice_no.replace("-", "").isalnum():
            errors.append("notice_no")
        if self.level not in ("watch", "stop_sail", "stop_lift", "clear"):
            errors.append("level")
        if isinstance(self.hours, bool) or not isinstance(self.hours, int):
            errors.append("hours")
        elif self.hours < 0 or self.hours > 72:
            errors.append("hours")
        return errors

    def to_dict(self):
        return {"notice_no": self.notice_no, "level": self.level, "hours": self.hours}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["notice_no"], data["level"], data["hours"])

    def summary(self):
        return "WeatherHold:" + str(self.notice_no)

    def blocking(self):
        """禁航或禁吊。"""
        return self.level in ("stop_sail", "stop_lift")

