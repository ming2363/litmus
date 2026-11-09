"""冷箱在港台账。温度用十分之一摄氏度的整数，时间和别的模块一样用分钟。"""

from typing import Dict, List, Optional, Tuple

Reading = Tuple[int, int]  # 分钟, 十分之一摄氏度
Event = Tuple[int, str, str]


class Box:
    def __init__(self, box_id: str, cargo: str, setpoint: int) -> None:
        if not box_id or not cargo:
            raise ValueError("箱号和货类不能为空")
        if type(setpoint) is not int:
            raise ValueError("设定温度必须是整数")
        self.box_id = box_id
        self.cargo = cargo
        self.setpoint = setpoint
        self.plugged: Optional[int] = None
        self.readings: List[Reading] = []
        self.events: List[Event] = []

    def plug(self, minute: int, lane: str) -> None:
        if self.plugged is not None:
            raise ValueError("冷箱已经插电")
        if type(minute) is not int or not lane:
            raise ValueError("插电参数不合法")
        self.plugged = minute
        self.events.append((minute, "插电", lane))

    def unplug(self, minute: int) -> None:
        if self.plugged is None:
            raise ValueError("冷箱没有插电")
        if minute < self.plugged:
            raise ValueError("拔电早于插电")
        self.events.append((minute, "拔电", ""))
        self.plugged = None

    def note(self, minute: int, value: int) -> None:
        if type(minute) is not int or type(value) is not int:
            raise ValueError("抄表不合法")
        if self.readings and minute < self.readings[-1][0]:
            raise ValueError("抄表时间倒退")
        self.readings.append((minute, value))

    def retarget(self, minute: int, setpoint: int) -> None:
        if type(setpoint) is not int:
            raise ValueError("设定温度必须是整数")
        self.setpoint = setpoint
        self.events.append((minute, "改设定", str(setpoint)))


# 货类允许的设定范围，十分之一摄氏度，含两端。
BANDS = {
    "冻肉": (-250, -180),
    "冻鱼": (-220, -180),
    "香蕉": (130, 145),
    "药品": (20, 80),
    "巧克力": (140, 180),
}

# 偏离设定超过这个十分之一度，记一次超温。
EXCURSION = {
    "冻肉": 15,
    "冻鱼": 12,
    "香蕉": 8,
    "药品": 5,
    "巧克力": 10,
}


def band_ok(cargo: str, setpoint: int) -> bool:
    low, high = BANDS[cargo]
    return low <= setpoint <= high


def excursion_limit(cargo: str) -> int:
    if cargo not in EXCURSION:
        raise KeyError(cargo)
    return EXCURSION[cargo]


class Ledger:
    def __init__(self) -> None:
        self._boxes: Dict[str, Box] = {}

    def receive(self, box_id: str, cargo: str, setpoint: int) -> None:
        if box_id in self._boxes:
            raise ValueError("箱号重复")
        if cargo not in BANDS:
            raise ValueError("未知货类")
        if not band_ok(cargo, setpoint):
            raise ValueError("设定温度超出货类范围")
        self._boxes[box_id] = Box(box_id, cargo, setpoint)

    def get(self, box_id: str) -> Box:
        box = self._boxes.get(box_id)
        if box is None:
            raise KeyError(box_id)
        return box

    def ids(self) -> List[str]:
        return sorted(self._boxes)

    def plugged(self) -> List[str]:
        return sorted(box_id for box_id, box in self._boxes.items() if box.plugged is not None)

    def excursions(self, box_id: str) -> List[Reading]:
        box = self.get(box_id)
        limit = excursion_limit(box.cargo)
        return [row for row in box.readings if abs(row[1] - box.setpoint) > limit]

    def stable_run(self, box_id: str) -> int:
        """连续未超温的抄表次数，从最后一条往前数。"""
        box = self.get(box_id)
        limit = excursion_limit(box.cargo)
        run = 0
        for _minute, value in reversed(box.readings):
            if abs(value - box.setpoint) > limit:
                break
            run += 1
        return run

    def worst(self, cargo: str) -> Optional[Tuple[str, int]]:
        """该货类里偏离设定最大的箱。并列取箱号较小者。"""
        best: Optional[Tuple[str, int]] = None
        for box_id, box in self._boxes.items():
            if box.cargo != cargo or not box.readings:
                continue
            delta = max(abs(value - box.setpoint) for _minute, value in box.readings)
            if best is None or delta > best[1] or (delta == best[1] and box_id < best[0]):
                best = (box_id, delta)
        return best

    def lane_events(self, lane: str) -> List[Event]:
        rows: List[Event] = []
        for box in self._boxes.values():
            for minute, kind, detail in box.events:
                if kind == "插电" and detail == lane:
                    rows.append((minute, box.box_id, kind))
        rows.sort()
        return rows


def mean_reading(box: Box) -> Optional[int]:
    if not box.readings:
        return None
    total = sum(value for _minute, value in box.readings)
    return total // len(box.readings)


def time_on_power(box: Box, now: int) -> int:
    """当前仍插电时，用 now 当作结束分钟。"""
    if box.plugged is None:
        # 用最后一次拔电减最后一次插电。多次插拔按事件成对相减。
        minutes = 0
        opened: Optional[int] = None
        for minute, kind, _detail in box.events:
            if kind == "插电":
                opened = minute
            elif kind == "拔电" and opened is not None:
                minutes += minute - opened
                opened = None
        return minutes
    base = 0
    opened = None
    for minute, kind, _detail in box.events:
        if kind == "插电":
            opened = minute
        elif kind == "拔电" and opened is not None:
            base += minute - opened
            opened = None
    if opened is None:
        return base
    if now < opened:
        raise ValueError("当前分钟早于插电")
    return base + (now - opened)
