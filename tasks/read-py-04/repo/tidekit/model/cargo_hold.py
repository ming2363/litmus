"""船舱货量"""


class CargoHold(object):
    """船舱货量"""

    def __init__(self, hold_no, capacity_t, loaded_t, cargo):
        self.hold_no = hold_no
        self.capacity_t = capacity_t
        self.loaded_t = loaded_t
        self.cargo = cargo

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.hold_no, str) or not (2 <= len(self.hold_no) <= 16):
            errors.append("hold_no")
        elif not self.hold_no.replace("-", "").isalnum():
            errors.append("hold_no")
        if isinstance(self.capacity_t, bool) or not isinstance(self.capacity_t, int):
            errors.append("capacity_t")
        elif self.capacity_t < 1 or self.capacity_t > 20000:
            errors.append("capacity_t")
        if isinstance(self.loaded_t, bool) or not isinstance(self.loaded_t, int):
            errors.append("loaded_t")
        elif self.loaded_t < 0 or self.loaded_t > 20000:
            errors.append("loaded_t")
        if not isinstance(self.cargo, str) or not self.cargo.strip():
            errors.append("cargo")
        elif len(self.cargo.strip()) > 40:
            errors.append("cargo")
        return errors

    def to_dict(self):
        return {"hold_no": self.hold_no, "capacity_t": self.capacity_t, "loaded_t": self.loaded_t, "cargo": self.cargo}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["hold_no"], data["capacity_t"], data["loaded_t"], data["cargo"])

    def summary(self):
        return "CargoHold:" + str(self.hold_no)

    def free_tonnes(self):
        """剩余可装吨数，不为负。"""
        left = self.capacity_t - self.loaded_t
        if left < 0:
            return 0
        return left

