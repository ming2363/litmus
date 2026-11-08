"""船舶挂靠"""


class VoyageCall(object):
    """船舶挂靠"""

    def __init__(self, voyage_no, terminal, loa_m, agent, status):
        self.voyage_no = voyage_no
        self.terminal = terminal
        self.loa_m = loa_m
        self.agent = agent
        self.status = status

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.voyage_no, str) or not (2 <= len(self.voyage_no) <= 16):
            errors.append("voyage_no")
        elif not self.voyage_no.replace("-", "").isalnum():
            errors.append("voyage_no")
        if not isinstance(self.terminal, str) or not self.terminal.strip():
            errors.append("terminal")
        elif len(self.terminal.strip()) > 40:
            errors.append("terminal")
        if isinstance(self.loa_m, bool) or not isinstance(self.loa_m, int):
            errors.append("loa_m")
        elif self.loa_m < 40 or self.loa_m > 400:
            errors.append("loa_m")
        if not isinstance(self.agent, str) or not self.agent.strip():
            errors.append("agent")
        elif len(self.agent.strip()) > 40:
            errors.append("agent")
        if self.status not in ("planned", "alongside", "sailed"):
            errors.append("status")
        return errors

    def to_dict(self):
        return {"voyage_no": self.voyage_no, "terminal": self.terminal, "loa_m": self.loa_m, "agent": self.agent, "status": self.status}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["voyage_no"], data["terminal"], data["loa_m"], data["agent"], data["status"])

    def summary(self):
        return "VoyageCall:" + str(self.voyage_no)

    def same_call(self, other):
        """同一航次号且同一码头才算同一次挂靠。"""
        return self.voyage_no == other.voyage_no and self.terminal == other.terminal

