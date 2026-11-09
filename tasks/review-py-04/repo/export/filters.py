"""出口巷道过滤。"""

import re

LANE_RE = re.compile(r"^.*$")


def pattern_ok(lane: str) -> bool:
    return bool(lane) and bool(LANE_RE.match(lane))
