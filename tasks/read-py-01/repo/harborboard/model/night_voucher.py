"""夜班凭证"""


class NightVoucher(object):
    """夜班凭证"""

    def __init__(self, voucher_no, debit_fen, credit_fen, desk):
        self.voucher_no = voucher_no
        self.debit_fen = debit_fen
        self.credit_fen = credit_fen
        self.desk = desk

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.voucher_no, str) or not (2 <= len(self.voucher_no) <= 16):
            errors.append("voucher_no")
        elif not self.voucher_no.replace("-", "").isalnum():
            errors.append("voucher_no")
        if isinstance(self.debit_fen, bool) or not isinstance(self.debit_fen, int) or self.debit_fen < 0:
            errors.append("debit_fen")
        if isinstance(self.credit_fen, bool) or not isinstance(self.credit_fen, int) or self.credit_fen < 0:
            errors.append("credit_fen")
        if not isinstance(self.desk, str) or not self.desk.strip():
            errors.append("desk")
        elif len(self.desk.strip()) > 40:
            errors.append("desk")
        return errors

    def to_dict(self):
        return {"voucher_no": self.voucher_no, "debit_fen": self.debit_fen, "credit_fen": self.credit_fen, "desk": self.desk}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["voucher_no"], data["debit_fen"], data["credit_fen"], data["desk"])

    def summary(self):
        return "NightVoucher:" + str(self.voucher_no)

    def signed(self):
        """借贷都非负且相等才算签平。"""
        return self.debit_fen >= 0 and self.debit_fen == self.credit_fen

