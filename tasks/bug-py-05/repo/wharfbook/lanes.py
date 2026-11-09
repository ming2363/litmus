"""巷道拓扑。长度单位是米，和占用账本的分钟无关。"""

from typing import Dict, Iterable, List, Optional, Set, Tuple


class Lane:
    def __init__(self, code: str, length_m: int, depth_cm: int, plugs: int) -> None:
        if not code or length_m <= 0 or depth_cm <= 0 or plugs < 0:
            raise ValueError("巷道参数不合法")
        self.code = code
        self.length_m = length_m
        self.depth_cm = depth_cm
        self.plugs = plugs
        self.neighbors: List[str] = []


class YardMap:
    """北港一号堆场的巷道图。"""

    def __init__(self) -> None:
        self._lanes: Dict[str, Lane] = {}

    def add(self, lane: Lane) -> None:
        if lane.code in self._lanes:
            raise ValueError("巷道重复: {}".format(lane.code))
        self._lanes[lane.code] = lane

    def link(self, left: str, right: str) -> None:
        if left == right:
            raise ValueError("巷道不能连到自己")
        self._require(left).neighbors.append(right)
        self._require(right).neighbors.append(left)

    def _require(self, code: str) -> Lane:
        lane = self._lanes.get(code)
        if lane is None:
            raise KeyError(code)
        return lane

    def codes(self) -> List[str]:
        return sorted(self._lanes)

    def plugs(self, code: str) -> int:
        return self._require(code).plugs

    def depth_cm(self, code: str) -> int:
        return self._require(code).depth_cm

    def fits(self, code: str, loa_m: int, draft_cm: int) -> bool:
        lane = self._require(code)
        return loa_m <= lane.length_m and draft_cm <= lane.depth_cm

    def hops(self, origin: str, limit: int) -> Dict[str, int]:
        """从原点出发、步数不超过 limit 的巷道。"""
        if limit < 0:
            raise ValueError("步数不能为负")
        self._require(origin)
        seen = {origin: 0}
        frontier = [origin]
        while frontier:
            current = frontier.pop(0)
            if seen[current] == limit:
                continue
            for nxt in self._lanes[current].neighbors:
                if nxt in seen:
                    continue
                seen[nxt] = seen[current] + 1
                frontier.append(nxt)
        return seen

    def component(self, origin: str) -> Set[str]:
        return set(self.hops(origin, 10 ** 6))

    def dead_ends(self) -> List[str]:
        return sorted(code for code, lane in self._lanes.items() if len(lane.neighbors) <= 1)


def north_yard() -> YardMap:
    yard = YardMap()
    specs = (
        ("A", 280, 1250, 24),
        ("B", 280, 1250, 24),
        ("C", 320, 1400, 36),
        ("D", 210, 1100, 12),
        ("E", 180, 980, 8),
        ("F", 260, 1200, 18),
        ("G", 300, 1350, 30),
        ("H", 160, 900, 0),
    )
    for code, length_m, depth_cm, plugs in specs:
        yard.add(Lane(code, length_m, depth_cm, plugs))
    for left, right in (("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("C", "F"), ("F", "G"), ("G", "H")):
        yard.link(left, right)
    return yard


def lanes_accepting(loa_m: int, draft_cm: int, yard: Optional[YardMap] = None) -> List[str]:
    host = yard if yard is not None else north_yard()
    return [code for code in host.codes() if host.fits(code, loa_m, draft_cm)]


def plug_budget(codes: Iterable[str], yard: Optional[YardMap] = None) -> int:
    host = yard if yard is not None else north_yard()
    return sum(host.plugs(code) for code in codes)
