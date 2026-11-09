"""配件库。预约和出库按件计数，和分钟区间不是同一套数。"""

from typing import Dict, List, Tuple


class Bin:
    def __init__(self, sku: str, on_hand: int, reorder_at: int) -> None:
        if not sku or on_hand < 0 or reorder_at < 0:
            raise ValueError("库位参数不合法")
        self.sku = sku
        self.on_hand = on_hand
        self.reorder_at = reorder_at
        self.reserved = 0

    def free(self) -> int:
        return self.on_hand - self.reserved

    def needs_reorder(self) -> bool:
        return self.free() <= self.reorder_at


class Store:
    def __init__(self) -> None:
        self._bins: Dict[str, Bin] = {}
        self._log: List[Tuple[str, str, int]] = []

    def put(self, sku: str, on_hand: int, reorder_at: int) -> None:
        if sku in self._bins:
            raise ValueError("库位已存在")
        self._bins[sku] = Bin(sku, on_hand, reorder_at)

    def receive(self, sku: str, count: int) -> None:
        bin_ = self._require(sku)
        if type(count) is not int or count <= 0:
            raise ValueError("入库数量不合法")
        bin_.on_hand += count
        self._log.append(("入库", sku, count))

    def reserve(self, sku: str, count: int) -> None:
        bin_ = self._require(sku)
        if type(count) is not int or count <= 0:
            raise ValueError("预占数量不合法")
        if bin_.free() < count:
            raise ValueError("可预占数量不足")
        bin_.reserved += count
        self._log.append(("预占", sku, count))

    def release(self, sku: str, count: int) -> None:
        bin_ = self._require(sku)
        if type(count) is not int or count <= 0 or count > bin_.reserved:
            raise ValueError("释放数量不合法")
        bin_.reserved -= count
        self._log.append(("释放", sku, count))

    def issue(self, sku: str, count: int) -> None:
        """把已经预占的件出库。"""
        bin_ = self._require(sku)
        if type(count) is not int or count <= 0 or count > bin_.reserved:
            raise ValueError("出库数量不合法")
        bin_.reserved -= count
        bin_.on_hand -= count
        self._log.append(("出库", sku, count))

    def _require(self, sku: str) -> Bin:
        bin_ = self._bins.get(sku)
        if bin_ is None:
            raise KeyError(sku)
        return bin_

    def snapshot(self) -> List[Tuple[str, int, int]]:
        rows = []
        for sku in sorted(self._bins):
            bin_ = self._bins[sku]
            rows.append((sku, bin_.on_hand, bin_.reserved))
        return rows

    def reorder_list(self) -> List[str]:
        return sorted(sku for sku, bin_ in self._bins.items() if bin_.needs_reorder())

    def log(self) -> List[Tuple[str, str, int]]:
        return list(self._log)


def opening_store() -> Store:
    store = Store()
    for sku, on_hand, reorder_at in (
        ("钢丝绳", 16, 4),
        ("滑轮", 40, 8),
        ("制动片", 24, 6),
        ("电控模块", 6, 2),
        ("密封圈", 80, 20),
        ("润滑脂", 30, 10),
        ("限位开关", 18, 4),
        ("接触器", 12, 3),
    ):
        store.put(sku, on_hand, reorder_at)
    return store


def reserve_kit(store: Store, lines: List[Tuple[str, int]]) -> List[str]:
    """能预占的先预占，返回没占上的配件名。已经占上的不回滚。"""
    missing = []
    for sku, count in lines:
        try:
            store.reserve(sku, count)
        except (KeyError, ValueError):
            missing.append(sku)
    return missing
