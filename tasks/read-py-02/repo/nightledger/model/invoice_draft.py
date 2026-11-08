"""费用草稿"""


class InvoiceDraft(object):
    """费用草稿"""

    def __init__(self, invoice_no, payer, due_fen, paid_fen):
        self.invoice_no = invoice_no
        self.payer = payer
        self.due_fen = due_fen
        self.paid_fen = paid_fen

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.invoice_no, str) or not (2 <= len(self.invoice_no) <= 16):
            errors.append("invoice_no")
        elif not self.invoice_no.replace("-", "").isalnum():
            errors.append("invoice_no")
        if not isinstance(self.payer, str) or not self.payer.strip():
            errors.append("payer")
        elif len(self.payer.strip()) > 40:
            errors.append("payer")
        if isinstance(self.due_fen, bool) or not isinstance(self.due_fen, int) or self.due_fen < 0:
            errors.append("due_fen")
        if isinstance(self.paid_fen, bool) or not isinstance(self.paid_fen, int) or self.paid_fen < 0:
            errors.append("paid_fen")
        return errors

    def to_dict(self):
        return {"invoice_no": self.invoice_no, "payer": self.payer, "due_fen": self.due_fen, "paid_fen": self.paid_fen}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["invoice_no"], data["payer"], data["due_fen"], data["paid_fen"])

    def summary(self):
        return "InvoiceDraft:" + str(self.invoice_no)

    def balance_fen(self):
        """应收减已收。"""
        return self.due_fen - self.paid_fen

