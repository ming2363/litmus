"""闸口小票"""


class GateTicket(object):
    """闸口小票"""

    def __init__(self, ticket_no, plate, status, axles):
        self.ticket_no = ticket_no
        self.plate = plate
        self.status = status
        self.axles = axles

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.ticket_no, str) or not (2 <= len(self.ticket_no) <= 16):
            errors.append("ticket_no")
        elif not self.ticket_no.replace("-", "").isalnum():
            errors.append("ticket_no")
        if not isinstance(self.plate, str) or not self.plate.strip():
            errors.append("plate")
        elif len(self.plate.strip()) > 40:
            errors.append("plate")
        if self.status not in ("open", "closed", "void"):
            errors.append("status")
        if isinstance(self.axles, bool) or not isinstance(self.axles, int):
            errors.append("axles")
        elif self.axles < 2 or self.axles > 8:
            errors.append("axles")
        return errors

    def to_dict(self):
        return {"ticket_no": self.ticket_no, "plate": self.plate, "status": self.status, "axles": self.axles}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["ticket_no"], data["plate"], data["status"], data["axles"])

    def summary(self):
        return "GateTicket:" + str(self.ticket_no)

    def open_ticket(self):
        """未核销且未作废。"""
        return self.status == "open"

