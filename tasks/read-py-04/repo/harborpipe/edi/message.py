"""北港报文。一行一种记录，字段用竖线分开。"""

from typing import Dict, List, Tuple

Record = Tuple[str, List[str]]


def split_line(line: str) -> Record:
    text = line.strip()
    if not text or text.startswith("#"):
        raise ValueError("空行")
    parts = text.split("|")
    return parts[0], parts[1:]


def require(fields: List[str], count: int, name: str) -> None:
    if len(fields) != count:
        raise ValueError("{} 需要 {} 个字段".format(name, count))


def parse_int(text: str, name: str) -> int:
    negative = text.startswith("-")
    digits = text[1:] if negative else text
    if not digits or not digits.isdigit():
        raise ValueError("{} 不是整数".format(name))
    if len(digits) > 1 and digits[0] == "0":
        raise ValueError("{} 不能有前导零".format(name))
    value = int(digits)
    return -value if negative else value


def parse_minute(text: str) -> int:
    """星期字母加四位时分，折成计划周分钟。周一是 A。"""
    if len(text) != 5 or text[0] not in "ABCDEFG":
        raise ValueError("时刻格式不对")
    hour = parse_int(text[1:3], "时")
    minute = parse_int(text[3:5], "分")
    if hour > 23 or minute > 59 or hour < 0 or minute < 0:
        raise ValueError("时刻超出范围")
    return "ABCDEFG".index(text[0]) * 1440 + hour * 60 + minute


class Message:
    """按记录顺序收一票装卸报文。"""

    def __init__(self) -> None:
        self.header: Dict[str, str] = {}
        self.voyage = ""
        self.boxes: List[Dict[str, object]] = []
        self._open: Dict[str, object] = {}

    def feed(self, line: str) -> None:
        kind, fields = split_line(line)
        handler = getattr(self, "_on_" + kind.lower(), None)
        if handler is None:
            raise ValueError("未知记录 {}".format(kind))
        handler(fields)

    def _on_unh(self, fields: List[str]) -> None:
        require(fields, 3, "UNH")
        if self.header:
            raise ValueError("报文头重复")
        if fields[1] not in ("BAPLIE", "COPRAR"):
            raise ValueError("报文类型不对")
        self.header = {"ref": fields[0], "type": fields[1], "version": fields[2]}

    def _on_bgm(self, fields: List[str]) -> None:
        require(fields, 2, "BGM")
        if not self.header:
            raise ValueError("还没有报文头")
        self.header["document"] = fields[0]
        self.header["name"] = fields[1]

    def _on_voy(self, fields: List[str]) -> None:
        require(fields, 3, "VOY")
        self.voyage = fields[0]
        self.header["vessel"] = fields[1]
        self.header["eta"] = str(parse_minute(fields[2]))

    def _on_eqd(self, fields: List[str]) -> None:
        require(fields, 4, "EQD")
        if self._open:
            raise ValueError("上一箱还没有结束")
        size, kind = fields[2], fields[3]
        if size not in ("20", "40", "45"):
            raise ValueError("尺寸不对")
        if kind not in ("GP", "RF", "RH", "TK"):
            raise ValueError("箱型不对")
        self._open = {"id": fields[0], "owner": fields[1], "size": size, "kind": kind}

    def _on_mea(self, fields: List[str]) -> None:
        require(fields, 2, "MEA")
        if not self._open:
            raise ValueError("重量没有所属的箱")
        weight = parse_int(fields[1], "重量")
        if weight <= 0 or weight > 40000:
            raise ValueError("重量超出范围")
        self._open["weight"] = weight

    def _on_tmp(self, fields: List[str]) -> None:
        require(fields, 2, "TMP")
        if not self._open:
            raise ValueError("温度没有所属的箱")
        if self._open.get("kind") not in ("RF", "RH"):
            raise ValueError("只有冷箱带温度")
        setpoint = parse_int(fields[1], "设定")
        if setpoint < -300 or setpoint > 300:
            raise ValueError("设定超出范围")
        self._open["setpoint"] = setpoint

    def _on_sel(self, fields: List[str]) -> None:
        require(fields, 1, "SEL")
        if not self._open:
            raise ValueError("铅封没有所属的箱")
        seal = fields[0]
        if not seal or len(seal) > 16:
            raise ValueError("铅封号不合法")
        seals = self._open.setdefault("seals", [])
        if not isinstance(seals, list):
            raise ValueError("铅封结构坏了")
        seals.append(seal)

    def _on_loc(self, fields: List[str]) -> None:
        require(fields, 2, "LOC")
        if not self._open:
            raise ValueError("位置没有所属的箱")
        role, code = fields
        if role not in ("POL", "POD", "YARD"):
            raise ValueError("位置角色不对")
        self._open[role.lower()] = code

    def _on_han(self, fields: List[str]) -> None:
        require(fields, 1, "HAN")
        if not self._open:
            raise ValueError("操作码没有所属的箱")
        if fields[0] not in ("LOAD", "DISC", "STAY", "TRANS"):
            raise ValueError("操作码不对")
        self._open["handling"] = fields[0]

    def _on_dtm(self, fields: List[str]) -> None:
        require(fields, 2, "DTM")
        if not self._open:
            raise ValueError("时间没有所属的箱")
        if fields[0] not in ("IN", "OUT"):
            raise ValueError("时间角色不对")
        self._open[fields[0].lower() + "_at"] = parse_minute(fields[1])

    def _on_nad(self, fields: List[str]) -> None:
        require(fields, 2, "NAD")
        if not self._open:
            raise ValueError("参与方没有所属的箱")
        if fields[0] not in ("SH", "CN", "CA"):
            raise ValueError("参与方角色不对")
        self._open["party_" + fields[0].lower()] = fields[1]

    def _on_eqa(self, fields: List[str]) -> None:
        """结束当前箱。"""
        require(fields, 0, "EQA") if False else None
        if len(fields) != 0:
            raise ValueError("EQA 不带字段")
        if not self._open:
            raise ValueError("没有待结束的箱")
        if "weight" not in self._open or "handling" not in self._open:
            raise ValueError("箱的重量或操作码缺失")
        self.boxes.append(self._open)
        self._open = {}

    def _on_unt(self, fields: List[str]) -> None:
        require(fields, 1, "UNT")
        if self._open:
            raise ValueError("还有箱没有结束")
        count = parse_int(fields[0], "箱数")
        if count != len(self.boxes):
            raise ValueError("箱数对不上")
        self.header["count"] = str(count)

    def finish(self) -> List[Dict[str, object]]:
        if self._open:
            raise ValueError("最后一箱没有结束")
        if not self.header or not self.voyage or "count" not in self.header:
            raise ValueError("报文不完整")
        return list(self.boxes)


def load_text(text: str) -> Message:
    message = Message()
    for line in text.splitlines():
        if line.strip():
            message.feed(line)
    return message
