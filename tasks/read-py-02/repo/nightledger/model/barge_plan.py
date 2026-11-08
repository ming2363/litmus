"""驳船计划"""


class BargePlan(object):
    """驳船计划"""

    def __init__(self, barge_no, status, tonnes):
        self.barge_no = barge_no
        self.status = status
        self.tonnes = tonnes

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.barge_no, str) or not (2 <= len(self.barge_no) <= 16):
            errors.append("barge_no")
        elif not self.barge_no.replace("-", "").isalnum():
            errors.append("barge_no")
        if self.status not in ("anchor", "in", "out"):
            errors.append("status")
        if isinstance(self.tonnes, bool) or not isinstance(self.tonnes, int):
            errors.append("tonnes")
        elif self.tonnes < 0 or self.tonnes > 8000:
            errors.append("tonnes")
        return errors

    def to_dict(self):
        return {"barge_no": self.barge_no, "status": self.status, "tonnes": self.tonnes}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["barge_no"], data["status"], data["tonnes"])

    def summary(self):
        return "BargePlan:" + str(self.barge_no)

    def waiting(self):
        """还在锚地等候。"""
        return self.status == "anchor"

