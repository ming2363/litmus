"""工班时段"""


class WorkerShift(object):
    """工班时段"""

    def __init__(self, worker_no, start_min, end_min, role):
        self.worker_no = worker_no
        self.start_min = start_min
        self.end_min = end_min
        self.role = role

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.worker_no, str) or not (2 <= len(self.worker_no) <= 16):
            errors.append("worker_no")
        elif not self.worker_no.replace("-", "").isalnum():
            errors.append("worker_no")
        if isinstance(self.start_min, bool) or not isinstance(self.start_min, int):
            errors.append("start_min")
        elif self.start_min < 0 or self.start_min > 1440:
            errors.append("start_min")
        if isinstance(self.end_min, bool) or not isinstance(self.end_min, int):
            errors.append("end_min")
        elif self.end_min < 0 or self.end_min > 1440:
            errors.append("end_min")
        if self.role not in ("signal", "tally", "driver"):
            errors.append("role")
        return errors

    def to_dict(self):
        return {"worker_no": self.worker_no, "start_min": self.start_min, "end_min": self.end_min, "role": self.role}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["worker_no"], data["start_min"], data["end_min"], data["role"])

    def summary(self):
        return "WorkerShift:" + str(self.worker_no)

    def overnight(self):
        """跨过午夜的班次。"""
        return self.end_min <= self.start_min

