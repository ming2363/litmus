"""贝位配载：箱位、堆重、冷箱插座和危品隔离。"""

from typing import Dict, List, Optional, Sequence, Tuple


ROWS = ("A", "B", "C", "D", "E", "F", "G", "H")
TIERS = (2, 4, 6, 8, 10, 12, 14, 16)
REEFER_ROWS = frozenset({"A", "B", "G", "H"})
DECK_TIER = 8

# 主危类, 副危类 -> 至少隔开的贝数。0 表示可以相邻，9 表示不能同船。
SEGREGATION: Dict[Tuple[str, str], int] = {
    ("1.4", "1.4"): 0,
    ("1.4", "3"): 1,
    ("2.1", "2.2"): 0,
    ("2.1", "3"): 1,
    ("2.1", "5.1"): 2,
    ("2.3", "3"): 2,
    ("2.3", "8"): 1,
    ("3", "3"): 0,
    ("3", "4.1"): 1,
    ("3", "5.1"): 2,
    ("3", "8"): 1,
    ("4.1", "5.1"): 2,
    ("5.1", "8"): 1,
    ("6.1", "8"): 1,
    ("7", "3"): 9,
    ("7", "8"): 9,
    ("8", "8"): 0,
}


class StowageError(ValueError):
    """配载输入不合法。"""


def _pair_key(left: str, right: str) -> Tuple[str, str]:
    if left <= right:
        return (left, right)
    return (right, left)


def bay_gap(class_a: str, class_b: str, limited: bool) -> int:
    """两种危类之间至少隔开的贝数。限量包装降一档，但不能降到负数。"""
    if not class_a or not class_b:
        return 0
    gap = SEGREGATION.get(_pair_key(class_a, class_b))
    if gap is None:
        gap = 1 if class_a != class_b else 0
    if limited and gap > 0 and gap < 9:
        gap -= 1
    return gap


class Box:
    """一只待配的箱子。"""

    def __init__(
        self,
        number: str,
        size: int,
        weight_kg: int,
        reefer: bool = False,
        imdg: str = "",
        limited: bool = False,
        over_high: bool = False,
        port_of_discharge: str = "",
    ) -> None:
        if size not in (20, 40):
            raise StowageError("只接受 20 或 40 英尺箱")
        if type(weight_kg) is not int or weight_kg <= 0:
            raise StowageError("重量必须是正整数千克")
        if reefer and size == 40 and weight_kg > 32000:
            raise StowageError("40 英尺冷箱超重")
        self.number = number.strip().upper()
        self.size = size
        self.weight_kg = weight_kg
        self.reefer = reefer
        self.imdg = imdg.strip()
        self.limited = limited
        self.over_high = over_high
        self.port_of_discharge = port_of_discharge.strip().upper()


class Slot:
    """一个 20 英尺箱位。40 英尺箱占用相邻两个奇数贝的同一排层。"""

    def __init__(self, bay: int, row: str, tier: int) -> None:
        if bay % 2 == 0 or bay < 1:
            raise StowageError("箱位贝号必须是正奇数")
        if row not in ROWS:
            raise StowageError("排号不存在")
        if tier not in TIERS:
            raise StowageError("层号不存在")
        self.bay = bay
        self.row = row
        self.tier = tier

    def key(self) -> Tuple[int, str, int]:
        return (self.bay, self.row, self.tier)

    def label(self) -> str:
        return "{:02d}{}{:02d}".format(self.bay, self.row, self.tier)


class Placed:
    def __init__(self, box: Box, slots: Sequence[Slot]) -> None:
        self.box = box
        self.slots = tuple(slots)


class Vessel:
    """一艘固定贝位的船。贝号 01 到 bay_count，只用奇数贝作 20 英尺位。"""

    def __init__(self, bay_count: int, stack_limit_kg: int, plugs_per_bay: int) -> None:
        if bay_count < 3 or bay_count % 2 == 0:
            raise StowageError("贝数必须是不小于 3 的奇数")
        self.bay_count = bay_count
        self.stack_limit_kg = stack_limit_kg
        self.plugs_per_bay = plugs_per_bay
        self._placed: Dict[Tuple[int, str, int], Placed] = {}
        self._by_number: Dict[str, Placed] = {}

    def odd_bays(self) -> List[int]:
        return list(range(1, self.bay_count + 1, 2))

    def occupied(self, slot: Slot) -> Optional[Placed]:
        return self._placed.get(slot.key())

    def plugs_used(self, bay: int) -> int:
        seen = set()
        for placed in self._by_number.values():
            if not placed.box.reefer:
                continue
            for slot in placed.slots:
                if slot.bay == bay:
                    seen.add(placed.box.number)
        return len(seen)

    def stack_weight(self, bay: int, row: str) -> int:
        total = 0
        seen = set()
        for placed in self._by_number.values():
            for slot in placed.slots:
                if slot.bay == bay and slot.row == row and placed.box.number not in seen:
                    total += placed.box.weight_kg
                    seen.add(placed.box.number)
        return total

    def _cover(self, box: Box, bay: int, row: str, tier: int) -> List[Slot]:
        if box.size == 20:
            return [Slot(bay, row, tier)]
        # 40 英尺箱的贝号写成中间的偶数，实际压住两侧奇数贝。
        left = bay
        right = bay + 2
        if right > self.bay_count:
            raise StowageError("40 英尺箱超出船尾")
        return [Slot(left, row, tier), Slot(right, row, tier)]

    def _support_ok(self, slots: Sequence[Slot]) -> bool:
        for slot in slots:
            if slot.tier == TIERS[0]:
                continue
            lower_tier = TIERS[TIERS.index(slot.tier) - 1]
            if self.occupied(Slot(slot.bay, slot.row, lower_tier)) is None:
                return False
        return True

    def _overheight_ok(self, box: Box, slots: Sequence[Slot]) -> bool:
        if not box.over_high:
            return True
        top = TIERS[-1]
        return all(slot.tier == top for slot in slots)

    def _reefer_ok(self, box: Box, slots: Sequence[Slot]) -> bool:
        if not box.reefer:
            return True
        if any(slot.row not in REEFER_ROWS for slot in slots):
            return False
        bays = {slot.bay for slot in slots}
        for bay in bays:
            if self.plugs_used(bay) >= self.plugs_per_bay:
                return False
        return True

    def _weight_ok(self, box: Box, slots: Sequence[Slot]) -> bool:
        # 40 英尺箱的重量按两个 20 英尺位各计一次，堆重限制也按位计算。
        share = box.weight_kg if box.size == 20 else box.weight_kg
        for slot in slots:
            if self.stack_weight(slot.bay, slot.row) + share > self.stack_limit_kg:
                return False
        return True

    def _hazard_ok(self, box: Box, slots: Sequence[Slot]) -> bool:
        if not box.imdg:
            return True
        for placed in self._by_number.values():
            if not placed.box.imdg:
                continue
            need = bay_gap(box.imdg, placed.box.imdg, box.limited and placed.box.limited)
            if need >= 9:
                return False
            for mine in slots:
                for other in placed.slots:
                    if abs(mine.bay - other.bay) // 2 < need:
                        return False
        return True

    def _visibility_ok(self, box: Box, slots: Sequence[Slot]) -> bool:
        # 船首前三个奇数贝的甲板上，非冷箱不得超过甲板以上两层。
        for slot in slots:
            if slot.bay <= 5 and slot.tier > DECK_TIER + 4 and not box.reefer:
                return False
        return True

    def _discharge_ok(self, box: Box, slots: Sequence[Slot]) -> bool:
        """后卸的港口不能压在先卸的港口上面。空港口视为可压任何港。"""
        if not box.port_of_discharge:
            return True
        for slot in slots:
            if slot.tier == TIERS[0]:
                continue
            lower = self.occupied(Slot(slot.bay, slot.row, TIERS[TIERS.index(slot.tier) - 1]))
            if lower is None or not lower.box.port_of_discharge:
                continue
            if lower.box.port_of_discharge < box.port_of_discharge:
                return False
        return True

    def can_place(self, box: Box, bay: int, row: str, tier: int) -> Optional[str]:
        if box.number in self._by_number:
            return "箱号重复"
        try:
            slots = self._cover(box, bay, row, tier)
        except StowageError as exc:
            return str(exc)
        for slot in slots:
            if self.occupied(slot) is not None:
                return "箱位已被占用"
        if not self._support_ok(slots):
            return "悬空"
        if not self._overheight_ok(box, slots):
            return "超高箱不在顶层"
        if not self._reefer_ok(box, slots):
            return "冷箱插座或排位不够"
        if not self._weight_ok(box, slots):
            return "堆重超限"
        if not self._hazard_ok(box, slots):
            return "危品隔离不够"
        if not self._visibility_ok(box, slots):
            return "船首视线被挡"
        if not self._discharge_ok(box, slots):
            return "卸货港被倒压"
        return None

    def place(self, box: Box, bay: int, row: str, tier: int) -> Placed:
        reason = self.can_place(box, bay, row, tier)
        if reason is not None:
            raise StowageError(reason)
        placed = Placed(box, self._cover(box, bay, row, tier))
        for slot in placed.slots:
            self._placed[slot.key()] = placed
        self._by_number[box.number] = placed
        return placed

    def remove(self, number: str) -> Placed:
        placed = self._by_number.pop(number.strip().upper(), None)
        if placed is None:
            raise StowageError("船上没有这只箱")
        for slot in placed.slots:
            self._placed.pop(slot.key(), None)
        return placed

    def suggest(self, box: Box) -> Optional[Tuple[int, str, int]]:
        """从船尾向船首、从底层向上找第一个能放的位置。"""
        bays = list(reversed(self.odd_bays()))
        if box.size == 40:
            bays = [bay for bay in bays if bay + 2 <= self.bay_count]
        for tier in TIERS:
            for row in ROWS:
                for bay in bays:
                    if self.can_place(box, bay, row, tier) is None:
                        return (bay, row, tier)
        return None

    def load_all(self, boxes: Sequence[Box]) -> List[Tuple[str, str]]:
        """按重量从大到小自动落位。返回 (箱号, 结果) ，结果是箱位标签或拒绝原因。"""
        ordered = sorted(boxes, key=lambda item: (-item.weight_kg, item.number))
        report: List[Tuple[str, str]] = []
        for box in ordered:
            found = self.suggest(box)
            if found is None:
                report.append((box.number, "没有箱位"))
                continue
            bay, row, tier = found
            self.place(box, bay, row, tier)
            placed = self._by_number[box.number]
            report.append((box.number, "+".join(slot.label() for slot in placed.slots)))
        return report


def lashing_force(weight_kg: int, tier: int, wind_mps: int) -> int:
    """粗算绑扎水平力，单位牛顿。风越大、层越高，力越大。"""
    if wind_mps < 0 or tier not in TIERS:
        raise StowageError("绑扎参数不合法")
    height = TIERS.index(tier) + 1
    return weight_kg * (2 + height) + wind_mps * wind_mps * height * 3


def lashing_ok(weight_kg: int, tier: int, wind_mps: int, swl_newton: int) -> bool:
    return lashing_force(weight_kg, tier, wind_mps) <= swl_newton


def vertical_moment(vessel: Vessel) -> int:
    """以船中为原点的纵向重量矩。船首为正。"""
    mid = (vessel.bay_count + 1) / 2
    moment = 0
    for placed in vessel._by_number.values():
        bay = sum(slot.bay for slot in placed.slots) / len(placed.slots)
        moment += int(placed.box.weight_kg * (bay - mid))
    return moment


def gm_estimate(vessel: Vessel, light_kg: int, light_vcg: int, km_cm: int) -> int:
    """用厘米表示的初稳性高度近似值。压载不在这张表里。"""
    cargo = 0
    cargo_moment = 0
    for placed in vessel._by_number.values():
        vcg = max(slot.tier for slot in placed.slots) * 15
        cargo += placed.box.weight_kg
        cargo_moment += placed.box.weight_kg * vcg
    total = light_kg + cargo
    if total <= 0:
        raise StowageError("排水量必须为正")
    kg = (light_kg * light_vcg + cargo_moment) // total
    return km_cm - kg


def crane_split(vessel: Vessel) -> Tuple[List[int], List[int]]:
    """把奇数贝切成两段，使两段已配重量尽量接近。"""
    bays = vessel.odd_bays()
    weights = []
    for bay in bays:
        total = 0
        seen = set()
        for placed in vessel._by_number.values():
            if placed.box.number in seen:
                continue
            if any(slot.bay == bay for slot in placed.slots):
                total += placed.box.weight_kg
                seen.add(placed.box.number)
        weights.append(total)
    best_index = 0
    best_gap = None
    running = 0
    whole = sum(weights)
    for index, weight in enumerate(weights[:-1]):
        running += weight
        gap = abs(running - (whole - running))
        if best_gap is None or gap < best_gap:
            best_gap = gap
            best_index = index
    return (bays[: best_index + 1], bays[best_index + 1 :])


def departure_notes(vessel: Vessel, wind_mps: int, swl_newton: int, min_gm_cm: int, light_kg: int, light_vcg: int, km_cm: int) -> List[str]:
    notes: List[str] = []
    gm = gm_estimate(vessel, light_kg, light_vcg, km_cm)
    if gm < min_gm_cm:
        notes.append("初稳性不足")
    if abs(vertical_moment(vessel)) > vessel.stack_limit_kg * vessel.bay_count:
        notes.append("纵倾力矩偏大")
    for placed in vessel._by_number.values():
        tier = max(slot.tier for slot in placed.slots)
        if not lashing_ok(placed.box.weight_kg, tier, wind_mps, swl_newton):
            notes.append("绑扎不足:" + placed.box.number)
    if not notes:
        notes.append("可以离泊")
    return notes
