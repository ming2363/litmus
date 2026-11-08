"""航道水深"""


class ChannelDraft(object):
    """航道水深"""

    def __init__(self, channel, depth_m, survey_day):
        self.channel = channel
        self.depth_m = depth_m
        self.survey_day = survey_day

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.channel, str) or not (2 <= len(self.channel) <= 16):
            errors.append("channel")
        elif not self.channel.replace("-", "").isalnum():
            errors.append("channel")
        if isinstance(self.depth_m, bool) or not isinstance(self.depth_m, int):
            errors.append("depth_m")
        elif self.depth_m < 1 or self.depth_m > 30:
            errors.append("depth_m")
        if not isinstance(self.survey_day, str) or not self.survey_day.strip():
            errors.append("survey_day")
        elif len(self.survey_day.strip()) > 40:
            errors.append("survey_day")
        return errors

    def to_dict(self):
        return {"channel": self.channel, "depth_m": self.depth_m, "survey_day": self.survey_day}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["channel"], data["depth_m"], data["survey_day"])

    def summary(self):
        return "ChannelDraft:" + str(self.channel)

    def under_keel(self, draught_m):
        """富裕水深。"""
        return self.depth_m - draught_m

