"""燃油加注"""


class FuelIssue(object):
    """燃油加注"""

    def __init__(self, issue_no, issued_l, used_l, grade):
        self.issue_no = issue_no
        self.issued_l = issued_l
        self.used_l = used_l
        self.grade = grade

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.issue_no, str) or not (2 <= len(self.issue_no) <= 16):
            errors.append("issue_no")
        elif not self.issue_no.replace("-", "").isalnum():
            errors.append("issue_no")
        if isinstance(self.issued_l, bool) or not isinstance(self.issued_l, int):
            errors.append("issued_l")
        elif self.issued_l < 0 or self.issued_l > 500000:
            errors.append("issued_l")
        if isinstance(self.used_l, bool) or not isinstance(self.used_l, int):
            errors.append("used_l")
        elif self.used_l < 0 or self.used_l > 500000:
            errors.append("used_l")
        if not isinstance(self.grade, str) or not self.grade.strip():
            errors.append("grade")
        elif len(self.grade.strip()) > 40:
            errors.append("grade")
        return errors

    def to_dict(self):
        return {"issue_no": self.issue_no, "issued_l": self.issued_l, "used_l": self.used_l, "grade": self.grade}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["issue_no"], data["issued_l"], data["used_l"], data["grade"])

    def summary(self):
        return "FuelIssue:" + str(self.issue_no)

    def leftover_litre(self):
        """库存升数。"""
        left = self.issued_l - self.used_l
        if left < 0:
            return 0
        return left

