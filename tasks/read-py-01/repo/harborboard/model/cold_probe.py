"""温度探针"""


class ColdProbe(object):
    """温度探针"""

    def __init__(self, probe_no, seen_min, celsius, zone):
        self.probe_no = probe_no
        self.seen_min = seen_min
        self.celsius = celsius
        self.zone = zone

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.probe_no, str) or not (2 <= len(self.probe_no) <= 16):
            errors.append("probe_no")
        elif not self.probe_no.replace("-", "").isalnum():
            errors.append("probe_no")
        if isinstance(self.seen_min, bool) or not isinstance(self.seen_min, int):
            errors.append("seen_min")
        elif self.seen_min < 0 or self.seen_min > 200000:
            errors.append("seen_min")
        if isinstance(self.celsius, bool) or not isinstance(self.celsius, int):
            errors.append("celsius")
        elif self.celsius < -40 or self.celsius > 40:
            errors.append("celsius")
        if not isinstance(self.zone, str) or not self.zone.strip():
            errors.append("zone")
        elif len(self.zone.strip()) > 40:
            errors.append("zone")
        return errors

    def to_dict(self):
        return {"probe_no": self.probe_no, "seen_min": self.seen_min, "celsius": self.celsius, "zone": self.zone}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["probe_no"], data["seen_min"], data["celsius"], data["zone"])

    def summary(self):
        return "ColdProbe:" + str(self.probe_no)

    def stale(self, now_min, limit_min):
        """距最近采样超过阈值。"""
        return now_min - self.seen_min > limit_min

