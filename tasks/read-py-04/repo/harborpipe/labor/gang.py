"""工班编排：资质、休息、夜班和加班费。金额是分，时间是小时。"""

from typing import Dict, List, Optional, Sequence, Tuple


ROLES = ("司机", "指挥", "绑扎", "理货", "拖车")
# 角色 -> (时薪分, 至少持有的证件)
ROLE_PAY: Dict[str, Tuple[int, Tuple[str, ...]]] = {
    "司机": (8000, ("场桥", "体检")),
    "指挥": (6500, ("指挥", "体检")),
    "绑扎": (5200, ("绑扎", "体检")),
    "理货": (4800, ("理货",)),
    "拖车": (5000, ("拖车", "体检")),
}

# 工班模板：船型 -> 每个角色需要的人数
TEMPLATE: Dict[str, Dict[str, int]] = {
    "驳船": {"司机": 1, "指挥": 1, "绑扎": 2, "理货": 1, "拖车": 2},
    "集箱": {"司机": 2, "指挥": 2, "绑扎": 4, "理货": 2, "拖车": 4},
    "冷箱": {"司机": 2, "指挥": 2, "绑扎": 4, "理货": 2, "拖车": 3},
    "件杂": {"司机": 1, "指挥": 2, "绑扎": 6, "理货": 2, "拖车": 2},
}


class GangError(ValueError):
    """工班输入不合法。"""


class Worker:
    def __init__(self, worker_id: str, name: str, tickets: Sequence[str], night_count: int = 0) -> None:
        self.worker_id = worker_id.strip().upper()
        self.name = name.strip()
        self.tickets = frozenset(item.strip() for item in tickets if item.strip())
        self.night_count = night_count
        if not self.worker_id or not self.name:
            raise GangError("工号和姓名不能为空")
        if night_count < 0:
            raise GangError("夜班次数不能为负")

    def can_do(self, role: str) -> bool:
        if role not in ROLE_PAY:
            return False
        _pay, need = ROLE_PAY[role]
        return all(ticket in self.tickets for ticket in need)


class Shift:
    """一段已经发生或计划中的出勤。小时用当天 0 到 48，允许跨到次日。"""

    def __init__(self, worker_id: str, start: int, end: int, role: str, night: bool) -> None:
        if role not in ROLES:
            raise GangError("岗位不存在")
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= 48:
            raise GangError("出勤时间不合法")
        self.worker_id = worker_id
        self.start = start
        self.end = end
        self.role = role
        self.night = night

    def hours(self) -> int:
        return self.end - self.start


def overlaps(left: Shift, right: Shift) -> bool:
    return left.start < right.end and right.start < left.end


def rest_ok(previous: Sequence[Shift], nxt: Shift, gap: int = 11) -> bool:
    """两段出勤之间至少隔开 gap 小时。只和同一人比较。"""
    for item in previous:
        if item.worker_id != nxt.worker_id:
            continue
        if overlaps(item, nxt):
            return False
        if item.end <= nxt.start and nxt.start - item.end < gap:
            return False
        if nxt.end <= item.start and item.start - nxt.end < gap:
            return False
    return True


def week_hours(previous: Sequence[Shift], worker_id: str) -> int:
    return sum(item.hours() for item in previous if item.worker_id == worker_id)


def overtime_bands(hours: int) -> List[Tuple[int, int]]:
    """把一段工时拆成 (小时数, 倍率千分比)。前 8 小时 1000，接下来 3 小时 1500，再往后 2000。"""
    if hours < 0:
        raise GangError("工时不能为负")
    bands = ((8, 1000), (3, 1500))
    remain = hours
    result: List[Tuple[int, int]] = []
    for width, rate in bands:
        take = remain if remain < width else width
        if take:
            result.append((take, rate))
        remain -= take
        if remain <= 0:
            return result
    if remain:
        result.append((remain, 2000))
    return result


def pay_cents(role: str, hours: int, night: bool, weather_stop: int) -> int:
    """天气停工仍支付停工小时的六成，并且不再算加班。其余小时走加班分段，夜班再加两成。"""
    if role not in ROLE_PAY:
        raise GangError("岗位不存在")
    if hours < 0 or weather_stop < 0 or weather_stop > hours:
        raise GangError("停工小时不合法")
    rate, _need = ROLE_PAY[role]
    stopped = weather_stop * rate * 600 // 1000
    worked = hours - weather_stop
    active = 0
    for width, multiplier in overtime_bands(worked):
        active += width * rate * multiplier // 1000
    if night:
        active = active * 1200 // 1000
        stopped = stopped * 1200 // 1000
    return active + stopped


class Roster:
    def __init__(self, workers: Sequence[Worker]) -> None:
        self.workers: Dict[str, Worker] = {}
        for worker in workers:
            if worker.worker_id in self.workers:
                raise GangError("工号重复")
            self.workers[worker.worker_id] = worker
        self.shifts: List[Shift] = []

    def candidates(self, role: str, start: int, end: int, night: bool, weekly_cap: int = 40) -> List[Worker]:
        found: List[Worker] = []
        for worker in self.workers.values():
            if not worker.can_do(role):
                continue
            trial = Shift(worker.worker_id, start, end, role, night)
            if not rest_ok(self.shifts, trial):
                continue
            if week_hours(self.shifts, worker.worker_id) + trial.hours() > weekly_cap:
                continue
            found.append(worker)
        found.sort(key=lambda item: (item.night_count if night else 0, week_hours(self.shifts, item.worker_id), item.worker_id))
        return found

    def assign(self, worker_id: str, start: int, end: int, role: str, night: bool, weekly_cap: int = 40) -> Shift:
        worker = self.workers.get(worker_id)
        if worker is None:
            raise GangError("没有这个工号")
        if not worker.can_do(role):
            raise GangError("资质不够")
        shift = Shift(worker_id, start, end, role, night)
        if not rest_ok(self.shifts, shift):
            raise GangError("休息时间不够")
        if week_hours(self.shifts, worker_id) + shift.hours() > weekly_cap:
            raise GangError("周工时超限")
        self.shifts.append(shift)
        if night:
            worker.night_count += 1
        return shift

    def fill(self, ship: str, start: int, end: int, night: bool) -> List[Tuple[str, str]]:
        """按模板把岗位填满。返回 (岗位, 工号或缺口说明)。"""
        if ship not in TEMPLATE:
            raise GangError("船型没有模板")
        report: List[Tuple[str, str]] = []
        for role, count in TEMPLATE[ship].items():
            for _index in range(count):
                options = self.candidates(role, start, end, night)
                if not options:
                    report.append((role, "缺人"))
                    continue
                chosen = options[0]
                self.assign(chosen.worker_id, start, end, role, night)
                report.append((role, chosen.worker_id))
        return report

    def payroll(self, weather_stop: int = 0) -> List[Tuple[str, int]]:
        """按人汇总本周工资。停工小时从每段出勤的末尾扣，扣完为止。"""
        remain = weather_stop
        totals: Dict[str, int] = {worker_id: 0 for worker_id in self.workers}
        for shift in self.shifts:
            stop = shift.hours() if remain > shift.hours() else remain
            remain -= stop
            totals[shift.worker_id] += pay_cents(shift.role, shift.hours(), shift.night, stop)
        rows = [(worker_id, totals[worker_id]) for worker_id in sorted(totals)]
        return rows

    def uncovered(self, ship: str) -> List[Tuple[str, int]]:
        if ship not in TEMPLATE:
            raise GangError("船型没有模板")
        have: Dict[str, int] = {role: 0 for role in ROLES}
        for shift in self.shifts:
            have[shift.role] += 1
        missing = []
        for role, count in TEMPLATE[ship].items():
            if have[role] < count:
                missing.append((role, count - have[role]))
        return missing


def substitute(worker: Worker, role: str) -> Optional[str]:
    """本人不能上这个岗时，看能不能改派到别的岗。按时薪从高到低试。"""
    if worker.can_do(role):
        return role
    ranked = sorted(ROLES, key=lambda item: ROLE_PAY[item][0], reverse=True)
    for other in ranked:
        if worker.can_do(other):
            return other
    return None


def fatigue_flag(shifts: Sequence[Shift], worker_id: str) -> str:
    """连续出勤超过 12 小时，或一夜班紧接一早班，标成疲劳。"""
    mine = [item for item in shifts if item.worker_id == worker_id]
    mine.sort(key=lambda item: item.start)
    for item in mine:
        if item.hours() > 12:
            return "单段过长"
    for previous, nxt in zip(mine, mine[1:]):
        if previous.night and not nxt.night and nxt.start - previous.end < 14:
            return "夜班接早班"
    return "正常"


def spread_nights(roster: Roster) -> int:
    """夜班次数的极差。没有人时返回 0。"""
    if not roster.workers:
        return 0
    counts = [worker.night_count for worker in roster.workers.values()]
    return max(counts) - min(counts)


def explain_pay(role: str, hours: int, night: bool, weather_stop: int) -> str:
    amount = pay_cents(role, hours, night, weather_stop)
    parts = []
    for width, multiplier in overtime_bands(max(0, hours - weather_stop)):
        parts.append("{}小时×{}".format(width, multiplier))
    night_text = "夜班" if night else "白班"
    return "{} {} {} 停工{} 合计{}分".format(role, night_text, "+".join(parts) or "无作业", weather_stop, amount)
