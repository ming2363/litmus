"""甚高频日志"""


class RadioLog(object):
    """甚高频日志"""

    def __init__(self, log_no, channel, party):
        self.log_no = log_no
        self.channel = channel
        self.party = party

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.log_no, str) or not (2 <= len(self.log_no) <= 16):
            errors.append("log_no")
        elif not self.log_no.replace("-", "").isalnum():
            errors.append("log_no")
        if isinstance(self.channel, bool) or not isinstance(self.channel, int):
            errors.append("channel")
        elif self.channel < 1 or self.channel > 88:
            errors.append("channel")
        if not isinstance(self.party, str) or not self.party.strip():
            errors.append("party")
        elif len(self.party.strip()) > 40:
            errors.append("party")
        return errors

    def to_dict(self):
        return {"log_no": self.log_no, "channel": self.channel, "party": self.party}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["log_no"], data["channel"], data["party"])

    def summary(self):
        return "RadioLog:" + str(self.log_no)

    def distress(self):
        """遇险频道。"""
        return self.channel == 16

