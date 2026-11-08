"""安全演习"""


class SafetyDrill(object):
    """安全演习"""

    def __init__(self, drill_no, present, required, open_items):
        self.drill_no = drill_no
        self.present = present
        self.required = required
        self.open_items = open_items

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.drill_no, str) or not (2 <= len(self.drill_no) <= 16):
            errors.append("drill_no")
        elif not self.drill_no.replace("-", "").isalnum():
            errors.append("drill_no")
        if isinstance(self.present, bool) or not isinstance(self.present, int):
            errors.append("present")
        elif self.present < 0 or self.present > 500:
            errors.append("present")
        if isinstance(self.required, bool) or not isinstance(self.required, int):
            errors.append("required")
        elif self.required < 1 or self.required > 500:
            errors.append("required")
        if isinstance(self.open_items, bool) or not isinstance(self.open_items, int):
            errors.append("open_items")
        elif self.open_items < 0 or self.open_items > 50:
            errors.append("open_items")
        return errors

    def to_dict(self):
        return {"drill_no": self.drill_no, "present": self.present, "required": self.required, "open_items": self.open_items}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["drill_no"], data["present"], data["required"], data["open_items"])

    def summary(self):
        return "SafetyDrill:" + str(self.drill_no)

    def passed(self):
        """到场人数够且没有未关闭项。"""
        return self.present >= self.required and self.open_items == 0

