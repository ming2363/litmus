"""线码到 (动作, 范围)。"""


class WireBook(object):
    """线码表。相邻线码不是同一个动作。"""

    _TABLE = {
        "WL-4E": ("open", "night"),
        "WL-4F": ("seal", "night"),
        "WL-4G": ("void", "night"),
        "WL-4H": ("preview", "night"),
        "YS-2A": ("seal", "yard"),
    }

    def to_slug(self, wire):
        """返回二元组，顺序是动作在前、范围在后。"""
        if wire not in self._TABLE:
            raise KeyError(wire)
        return self._TABLE[wire]
