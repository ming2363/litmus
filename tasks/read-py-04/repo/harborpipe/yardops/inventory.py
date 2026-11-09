"""贝位库存。层从 1 起，重箱不能压在轻箱上，冷箱只能放在带插头的贝。"""

from typing import Dict, List, Optional, Tuple

Slot = Tuple[int, int, int]  # 贝, 排, 层


class Occupant:
    def __init__(self, box_id: str, weight: int, reefer: bool, hazard: str) -> None:
        self.box_id = box_id
        self.weight = weight
        self.reefer = reefer
        self.hazard = hazard


class Bay:
    def __init__(self, index: int, rows: int, tiers: int, plug: bool, hazard_gap: int, max_weight: int) -> None:
        if rows <= 0 or tiers <= 0 or max_weight <= 0 or hazard_gap < 0:
            raise ValueError("贝位参数不合法")
        self.index = index
        self.rows = rows
        self.tiers = tiers
        self.plug = plug
        self.hazard_gap = hazard_gap
        self.max_weight = max_weight
        self._cells: Dict[Tuple[int, int], Occupant] = {}

    def _key(self, row: int, tier: int) -> Tuple[int, int]:
        if row < 1 or row > self.rows or tier < 1 or tier > self.tiers:
            raise ValueError("排或层超出贝位")
        return row, tier

    def get(self, row: int, tier: int) -> Optional[Occupant]:
        return self._cells.get(self._key(row, tier))

    def place(self, row: int, tier: int, box: Occupant) -> None:
        key = self._key(row, tier)
        if key in self._cells:
            raise ValueError("格位已占用")
        if box.reefer and not self.plug:
            raise ValueError("这个贝没有冷箱插头")
        if tier > 1 and (row, tier - 1) not in self._cells:
            raise ValueError("悬空")
        if tier > 1:
            below = self._cells[(row, tier - 1)]
            if box.weight > below.weight:
                raise ValueError("重箱压轻箱")
        if box.hazard and box.hazard != "NONE":
            self._check_hazard(row, tier, box.hazard)
        column_weight = box.weight
        for level in range(1, tier):
            column_weight += self._cells[(row, level)].weight
        if column_weight > self.max_weight:
            raise ValueError("列重超限")
        self._cells[key] = box

    def _check_hazard(self, row: int, tier: int, hazard: str) -> None:
        for (other_row, other_tier), other in self._cells.items():
            if not other.hazard or other.hazard == "NONE" or other.hazard == hazard:
                continue
            if abs(other_row - row) + abs(other_tier - tier) < self.hazard_gap:
                raise ValueError("危品距离不够")

    def lift(self, row: int, tier: int) -> Occupant:
        key = self._key(row, tier)
        if (row, tier + 1) in self._cells:
            raise ValueError("上面还有箱子")
        box = self._cells.pop(key, None)
        if box is None:
            raise KeyError((self.index, row, tier))
        return box

    def column_height(self, row: int) -> int:
        height = 0
        for tier in range(1, self.tiers + 1):
            if (row, tier) in self._cells:
                height = tier
        return height

    def reefer_count(self) -> int:
        return sum(1 for box in self._cells.values() if box.reefer)

    def find(self, box_id: str) -> Optional[Tuple[int, int]]:
        for (row, tier), box in self._cells.items():
            if box.box_id == box_id:
                return row, tier
        return None


class Yard:
    def __init__(self) -> None:
        self.bays = {
            1: Bay(1, 6, 4, False, 2, 90000),
            2: Bay(2, 6, 4, False, 2, 90000),
            3: Bay(3, 6, 5, True, 3, 110000),
            4: Bay(4, 8, 5, True, 3, 120000),
            5: Bay(5, 8, 4, True, 2, 100000),
            6: Bay(6, 6, 3, False, 4, 70000),
            7: Bay(7, 6, 5, True, 3, 110000),
            8: Bay(8, 8, 5, False, 2, 130000),
            9: Bay(9, 4, 3, True, 5, 60000),
            10: Bay(10, 8, 4, False, 2, 100000),
            11: Bay(11, 6, 4, True, 3, 95000),
            12: Bay(12, 6, 5, True, 4, 115000),
        }

    def place(self, bay: int, row: int, tier: int, box: Occupant) -> None:
        self.bays[bay].place(row, tier, box)

    def locate(self, box_id: str) -> Optional[Slot]:
        for index, bay in self.bays.items():
            found = bay.find(box_id)
            if found is not None:
                return index, found[0], found[1]
        return None

    def plug_bays(self) -> List[int]:
        return sorted(index for index, bay in self.bays.items() if bay.plug)

    def free_reefer_slots(self) -> List[Slot]:
        slots: List[Slot] = []
        for index, bay in self.bays.items():
            if not bay.plug:
                continue
            for row in range(1, bay.rows + 1):
                height = bay.column_height(row)
                if height < bay.tiers:
                    slots.append((index, row, height + 1))
        return slots

    def hazard_pairs(self) -> List[Tuple[str, str]]:
        boxes = []
        for bay in self.bays.values():
            for (row, tier), box in bay._cells.items():
                if box.hazard and box.hazard != "NONE":
                    boxes.append((bay.index, row, tier, box))
        pairs = []
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                left, right = boxes[i], boxes[j]
                if left[0] != right[0]:
                    continue
                if left[3].hazard == right[3].hazard:
                    continue
                distance = abs(left[1] - right[1]) + abs(left[2] - right[2])
                if distance < self.bays[left[0]].hazard_gap:
                    pairs.append((left[3].box_id, right[3].box_id))
        return pairs
