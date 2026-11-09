"""岸电表。读数是累计瓦时，允许回零，不允许无故倒退。"""

from typing import Dict, List, Optional, Tuple

Reading = Tuple[int, int]


class Meter:
    def __init__(self, meter_id: str, dial: int) -> None:
        if not meter_id or type(dial) is not int or dial <= 0:
            raise ValueError("电表参数不合法")
        self.meter_id = meter_id
        self.dial = dial
        self.rows: List[Reading] = []

    def read(self, minute: int, watt_hours: int) -> None:
        if type(minute) is not int or type(watt_hours) is not int:
            raise ValueError("抄表不合法")
        if watt_hours < 0 or watt_hours >= self.dial:
            raise ValueError("读数超出表盘")
        if self.rows and minute <= self.rows[-1][0]:
            raise ValueError("抄表时间没有前进")
        if self.rows:
            previous = self.rows[-1][1]
            if watt_hours < previous and watt_hours > previous // 10:
                raise ValueError("读数倒退又不是回零")
        self.rows.append((minute, watt_hours))

    def consumed(self, start: int, end: int) -> int:
        if start >= end:
            raise ValueError("区间不合法")
        window = [row for row in self.rows if start <= row[0] < end]
        if len(window) < 2:
            return 0
        total = 0
        for index in range(1, len(window)):
            prev = window[index - 1][1]
            cur = window[index][1]
            if cur >= prev:
                total += cur - prev
            else:
                total += (self.dial - prev) + cur
        return total


class Board:
    def __init__(self) -> None:
        self._meters: Dict[str, Meter] = {}

    def add(self, meter: Meter) -> None:
        if meter.meter_id in self._meters:
            raise ValueError("电表重复")
        self._meters[meter.meter_id] = meter

    def get(self, meter_id: str) -> Meter:
        meter = self._meters.get(meter_id)
        if meter is None:
            raise KeyError(meter_id)
        return meter

    def total(self, start: int, end: int) -> int:
        return sum(meter.consumed(start, end) for meter in self._meters.values())

    def busiest(self, start: int, end: int) -> Optional[str]:
        best_id = None
        best = -1
        for meter_id, meter in self._meters.items():
            used = meter.consumed(start, end)
            if used > best or (used == best and (best_id is None or meter_id < best_id)):
                best = used
                best_id = meter_id
        if best <= 0:
            return None
        return best_id


def share(board: Board, start: int, end: int) -> List[Tuple[str, int]]:
    rows = []
    for meter_id in sorted(board._meters):
        rows.append((meter_id, board.get(meter_id).consumed(start, end)))
    return rows
