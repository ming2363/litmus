"""泊位指泊：船长、吃水、桥吊能力和潮窗。时间是分钟。"""

from typing import Dict, List, Optional, Sequence, Tuple


class BerthError(ValueError):
    """指泊输入不合法。"""


class Berth:
    def __init__(self, code: str, length_m: int, depth_cm: int, cranes: int, reefer: bool) -> None:
        if length_m <= 0 or depth_cm <= 0 or cranes <= 0:
            raise BerthError("泊位尺度不合法")
        self.code = code.strip().upper()
        self.length_m = length_m
        self.depth_cm = depth_cm
        self.cranes = cranes
        self.reefer = reefer


class Call:
    """一条船的靠泊申请。"""

    def __init__(
        self,
        voyage: str,
        loa_m: int,
        draft_cm: int,
        eta: int,
        moves: int,
        reefer: bool = False,
        tide_windows: Sequence[Tuple[int, int]] = (),
    ) -> None:
        if loa_m <= 0 or draft_cm <= 0 or moves < 0 or eta < 0:
            raise BerthError("船期参数不合法")
        self.voyage = voyage.strip().upper()
        self.loa_m = loa_m
        self.draft_cm = draft_cm
        self.eta = eta
        self.moves = moves
        self.reefer = reefer
        self.tide_windows = tuple(tide_windows)
        for start, end in self.tide_windows:
            if type(start) is not int or type(end) is not int or start >= end:
                raise BerthError("潮窗不合法")


class Booking:
    def __init__(self, voyage: str, berth: str, start: int, end: int) -> None:
        self.voyage = voyage
        self.berth = berth
        self.start = start
        self.end = end


def service_minutes(moves: int, cranes: int, minutes_per_move: int = 3) -> int:
    """桥吊并行。至少留 60 分钟系解缆，作业不足一台桥吊时按一台算。"""
    if moves < 0 or cranes <= 0 or minutes_per_move <= 0:
        raise BerthError("作业参数不合法")
    used = cranes if moves >= cranes else 1
    work = (moves + used - 1) // used * minutes_per_move if moves else 0
    return work + 60


def fits(berth: Berth, call: Call, gap_m: int = 15) -> Optional[str]:
    if call.loa_m + gap_m > berth.length_m:
        return "船长加间隔超过泊位"
    if call.draft_cm + 50 > berth.depth_cm:
        return "吃水超过泊位水深"
    if call.reefer and not berth.reefer:
        return "泊位没有冷箱电源"
    return None


def earliest_tide(call: Call, ready: int, stay: int) -> Optional[int]:
    """开靠时刻必须落在某个潮窗内，并且整段停留都在该潮窗内。没有潮窗则随时可靠。"""
    if not call.tide_windows:
        return ready if ready >= call.eta else call.eta
    for start, end in sorted(call.tide_windows):
        begin = ready if ready > start else start
        if begin < call.eta:
            begin = call.eta
        if begin + stay <= end:
            return begin
    return None


class Quay:
    def __init__(self, berths: Sequence[Berth]) -> None:
        self.berths: Dict[str, Berth] = {}
        for berth in berths:
            if berth.code in self.berths:
                raise BerthError("泊位重复")
            self.berths[berth.code] = berth
        self.bookings: List[Booking] = []

    def busy_until(self, code: str) -> int:
        latest = 0
        for booking in self.bookings:
            if booking.berth == code and booking.end > latest:
                latest = booking.end
        return latest

    def clashes(self, code: str, start: int, end: int) -> bool:
        for booking in self.bookings:
            if booking.berth != code:
                continue
            if start < booking.end and booking.start < end:
                return True
        return False

    def options(self, call: Call) -> List[Tuple[int, str, int]]:
        """返回 (等待分钟, 泊位, 离泊时刻)，按等待再按泊位编号排序。"""
        found: List[Tuple[int, str, int]] = []
        for berth in self.berths.values():
            if fits(berth, call) is not None:
                continue
            stay = service_minutes(call.moves, berth.cranes)
            ready = self.busy_until(berth.code)
            start = earliest_tide(call, ready, stay)
            if start is None:
                continue
            end = start + stay
            if self.clashes(berth.code, start, end):
                # busy_until 已经取了最晚结束，正常不会再冲突。保险起见跳过。
                continue
            found.append((start - call.eta, berth.code, end))
        found.sort()
        return found

    def assign(self, call: Call) -> Booking:
        choices = self.options(call)
        if not choices:
            raise BerthError("没有可用泊位")
        _wait, code, end = choices[0]
        stay = end - (call.eta + _wait)
        start = end - stay
        booking = Booking(call.voyage, code, start, end)
        self.bookings.append(booking)
        return booking

    def plan(self, calls: Sequence[Call]) -> List[Tuple[str, str]]:
        """先到先靠。返回 (航次, 泊位或拒绝原因)。"""
        ordered = sorted(calls, key=lambda item: (item.eta, item.voyage))
        report: List[Tuple[str, str]] = []
        seen = {item.voyage for item in self.bookings}
        for call in ordered:
            if call.voyage in seen:
                report.append((call.voyage, "航次重复"))
                continue
            try:
                booking = self.assign(call)
            except BerthError as exc:
                report.append((call.voyage, str(exc)))
                continue
            seen.add(call.voyage)
            report.append((call.voyage, "{}@{}-{}".format(booking.berth, booking.start, booking.end)))
        return report

    def occupancy(self, start: int, end: int) -> List[Tuple[str, int]]:
        """各泊位在观察窗内被占用的分钟。"""
        if start >= end:
            raise BerthError("观察窗不合法")
        rows = []
        for code in sorted(self.berths):
            used = 0
            for booking in self.bookings:
                if booking.berth != code:
                    continue
                lo = booking.start if booking.start > start else start
                hi = booking.end if booking.end < end else end
                if lo < hi:
                    used += hi - lo
            rows.append((code, used))
        return rows

    def waiting(self) -> List[Tuple[str, int]]:
        rows = []
        for booking in self.bookings:
            rows.append((booking.voyage, booking.start))
        return rows


def explain_reject(berth: Berth, call: Call) -> str:
    reason = fits(berth, call)
    if reason is not None:
        return reason
    stay = service_minutes(call.moves, berth.cranes)
    if earliest_tide(call, call.eta, stay) is None:
        return "潮窗盖不住作业"
    return "可以靠"
