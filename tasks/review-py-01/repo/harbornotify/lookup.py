"""按编号找泊位。找不到时返回 None。"""


BERTHS = {
    "B01": {"code": "B01", "display_name": "顺岸1号", "zone": "east"},
    "B02": {"code": "B02", "display_name": "顺岸2号", "zone": "west"},
}


class BerthLookup(object):
    """内存底账。"""

    def find(self, code):
        """没有这个编号时返回 None。"""
        if code not in BERTHS:
            return None
        return dict(BERTHS[code])
