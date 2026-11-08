"""污染物接收"""


class WasteReceipt(object):
    """污染物接收"""

    def __init__(self, receipt_no, kg, free_kg, kind):
        self.receipt_no = receipt_no
        self.kg = kg
        self.free_kg = free_kg
        self.kind = kind

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.receipt_no, str) or not (2 <= len(self.receipt_no) <= 16):
            errors.append("receipt_no")
        elif not self.receipt_no.replace("-", "").isalnum():
            errors.append("receipt_no")
        if isinstance(self.kg, bool) or not isinstance(self.kg, int):
            errors.append("kg")
        elif self.kg < 0 or self.kg > 50000:
            errors.append("kg")
        if isinstance(self.free_kg, bool) or not isinstance(self.free_kg, int):
            errors.append("free_kg")
        elif self.free_kg < 0 or self.free_kg > 1000:
            errors.append("free_kg")
        if self.kind not in ("oil", "garbage", "sewage"):
            errors.append("kind")
        return errors

    def to_dict(self):
        return {"receipt_no": self.receipt_no, "kg": self.kg, "free_kg": self.free_kg, "kind": self.kind}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["receipt_no"], data["kg"], data["free_kg"], data["kind"])

    def summary(self):
        return "WasteReceipt:" + str(self.receipt_no)

    def needs_receipt(self):
        """超过免登记量就要回单。"""
        return self.kg > self.free_kg

