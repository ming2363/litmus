"""海关封志"""


class CustomsSeal(object):
    """海关封志"""

    def __init__(self, seal_no, box_no, broken):
        self.seal_no = seal_no
        self.box_no = box_no
        self.broken = broken

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.seal_no, str) or not (2 <= len(self.seal_no) <= 16):
            errors.append("seal_no")
        elif not self.seal_no.replace("-", "").isalnum():
            errors.append("seal_no")
        if not isinstance(self.box_no, str) or not self.box_no.strip():
            errors.append("box_no")
        elif len(self.box_no.strip()) > 40:
            errors.append("box_no")
        if not isinstance(self.broken, bool):
            errors.append("broken")
        return errors

    def to_dict(self):
        return {"seal_no": self.seal_no, "box_no": self.box_no, "broken": self.broken}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["seal_no"], data["box_no"], data["broken"])

    def summary(self):
        return "CustomsSeal:" + str(self.seal_no)

    def intact(self):
        """封志号完整且未拆。"""
        return bool(self.seal_no) and not self.broken

