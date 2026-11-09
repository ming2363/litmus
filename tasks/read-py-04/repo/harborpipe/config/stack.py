"""操作名到家族的层叠。"""

from typing import Optional, Sequence, Tuple

Pair = Tuple[str, str]
Layer = Tuple[int, str, Sequence[Pair]]


class Stack:
    """按层里的键解析家族。"""

    def __init__(self) -> None:
        self._layers: Tuple[Layer, ...] = (
            (10, "defaults", (("lane", "berth"), ("lane.reefer.audit", "yard"))),
            (30, "site", (("lane.reefer", "cold"),)),
            (30, "shift", (("lane.reefer.nightly", "night"),)),
            (50, "env", ()),
        )

    def family_for(self, operation: str) -> str:
        best_rank: Optional[Tuple[int, int, str]] = None
        best_family: Optional[str] = None
        for priority, name, pairs in self._layers:
            for key, family in pairs:
                if operation == key:
                    spec = 1000 + len(key)
                elif key and operation.startswith(key + "."):
                    spec = len(key)
                else:
                    continue
                rank = (priority, spec, name)
                if best_rank is None or rank > best_rank:
                    best_rank = rank
                    best_family = family
        if best_family is None:
            raise KeyError(operation)
        return best_family
