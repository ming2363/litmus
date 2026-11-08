"""泊位卡片"""


class BerthCard(object):
    """泊位卡片"""

    def __init__(self, code, name, length_m, draught_m, state, night_ok):
        self.code = code
        self.name = name
        self.length_m = length_m
        self.draught_m = draught_m
        self.state = state
        self.night_ok = night_ok

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.code, str) or not (2 <= len(self.code) <= 16):
            errors.append("code")
        elif not self.code.replace("-", "").isalnum():
            errors.append("code")
        if not isinstance(self.name, str) or not self.name.strip():
            errors.append("name")
        elif len(self.name.strip()) > 40:
            errors.append("name")
        if isinstance(self.length_m, bool) or not isinstance(self.length_m, int):
            errors.append("length_m")
        elif self.length_m < 30 or self.length_m > 420:
            errors.append("length_m")
        if isinstance(self.draught_m, bool) or not isinstance(self.draught_m, int):
            errors.append("draught_m")
        elif self.draught_m < 2 or self.draught_m > 20:
            errors.append("draught_m")
        if self.state not in ("active", "idle", "closed", "repair"):
            errors.append("state")
        if not isinstance(self.night_ok, bool):
            errors.append("night_ok")
        return errors

    def to_dict(self):
        return {"code": self.code, "name": self.name, "length_m": self.length_m, "draught_m": self.draught_m, "state": self.state, "night_ok": self.night_ok}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["code"], data["name"], data["length_m"], data["draught_m"], data["state"], data["night_ok"])

    def summary(self):
        return "BerthCard:" + str(self.code)

    def can_take(self, draught_m):
        """吃水不超过泊位限制且未关闭时可以靠。"""
        if self.state == "closed":
            return False
        if isinstance(draught_m, bool) or not isinstance(draught_m, int):
            raise TypeError("draught")
        return draught_m <= self.draught_m

