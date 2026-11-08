"""加水记录"""


class WaterSupply(object):
    """加水记录"""

    def __init__(self, supply_no, litres, point):
        self.supply_no = supply_no
        self.litres = litres
        self.point = point

    def validate(self):
        """返回错误字段名列表，空列表表示通过。"""
        errors = []
        if not isinstance(self.supply_no, str) or not (2 <= len(self.supply_no) <= 16):
            errors.append("supply_no")
        elif not self.supply_no.replace("-", "").isalnum():
            errors.append("supply_no")
        if isinstance(self.litres, bool) or not isinstance(self.litres, int):
            errors.append("litres")
        elif self.litres < 0 or self.litres > 2000000:
            errors.append("litres")
        if not isinstance(self.point, str) or not self.point.strip():
            errors.append("point")
        elif len(self.point.strip()) > 40:
            errors.append("point")
        return errors

    def to_dict(self):
        return {"supply_no": self.supply_no, "litres": self.litres, "point": self.point}

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise TypeError("data")
        return cls(data["supply_no"], data["litres"], data["point"])

    def summary(self):
        return "WaterSupply:" + str(self.supply_no)

    def tonnes(self):
        """按 1 吨 = 1000 升折算，向下取整。"""
        return self.litres // 1000

