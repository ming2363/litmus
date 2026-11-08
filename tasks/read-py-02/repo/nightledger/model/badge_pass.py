"""访客通行证"""


class BadgePass(object):
    """访客通行证"""

    def __init__(self, badge_no, holder, valid_day, lost):
        self.badge_no = badge_no
        self.holder = holder
        self.valid_day = valid_day
        self.lost = lost

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.badge_no, str) or not (2 <= len(self.badge_no) <= 16):
            errors.append("badge_no")
        elif not self.badge_no.replace("-", "").isalnum():
            errors.append("badge_no")
        if not isinstance(self.holder, str) or not self.holder.strip():
            errors.append("holder")
        elif len(self.holder.strip()) > 40:
            errors.append("holder")
        if not isinstance(self.valid_day, bool):
            errors.append("valid_day")
        if not isinstance(self.lost, bool):
            errors.append("lost")
        return errors

    def to_dict(self):
        return {"badge_no": self.badge_no, "holder": self.holder, "valid_day": self.valid_day, "lost": self.lost}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["badge_no"], data["holder"], data["valid_day"], data["lost"])

    def summary(self):
        return "BadgePass:" + str(self.badge_no)

    def day_pass(self):
        """当日有效且未挂失。"""
        return self.valid_day and not self.lost

