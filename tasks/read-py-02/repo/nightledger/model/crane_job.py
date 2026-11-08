"""门机作业"""


class CraneJob(object):
    """门机作业"""

    def __init__(self, job_no, crane, status, moves):
        self.job_no = job_no
        self.crane = crane
        self.status = status
        self.moves = moves

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.job_no, str) or not (2 <= len(self.job_no) <= 16):
            errors.append("job_no")
        elif not self.job_no.replace("-", "").isalnum():
            errors.append("job_no")
        if not isinstance(self.crane, str) or not self.crane.strip():
            errors.append("crane")
        elif len(self.crane.strip()) > 40:
            errors.append("crane")
        if self.status not in ("queued", "assigned", "working", "done"):
            errors.append("status")
        if isinstance(self.moves, bool) or not isinstance(self.moves, int):
            errors.append("moves")
        elif self.moves < 0 or self.moves > 800:
            errors.append("moves")
        return errors

    def to_dict(self):
        return {"job_no": self.job_no, "crane": self.crane, "status": self.status, "moves": self.moves}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["job_no"], data["crane"], data["status"], data["moves"])

    def summary(self):
        return "CraneJob:" + str(self.job_no)

    def busy(self):
        """作业中或已派工。"""
        return self.status in ("assigned", "working")

