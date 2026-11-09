"""靠泊通知单。把巷道、岸桥和班组拼成一页，分钟计划由调用方传入。"""

from typing import List, Sequence, Tuple

from wharfbook.crane import assignment
from wharfbook.roster import shortage
from wharfbook.shifts import gang_on, shift_of

Hold = Tuple[int, int, str]


def sheet(plan: Sequence[Hold], qualification_need: Sequence[Tuple[str, int]]) -> List[str]:
    if not plan:
        return ["本班无靠泊"]
    lanes = sorted({lane for _s, _e, lane in plan})
    cranes = assignment(lanes)
    lines = []
    for start, end, lane in plan:
        gang = gang_on(start // 1440, shift_of(start))
        crane = cranes.get(lane, "无岸桥")
        missing = shortage(start, qualification_need)
        if missing:
            gap = ",".join("{}缺{}".format(name, count) for name, count in missing)
        else:
            gap = "人力齐"
        lines.append(
            "巷道 {} 岸桥 {} 班组 {} {}-{} {}".format(lane, crane, gang, start, end, gap)
        )
    return lines
