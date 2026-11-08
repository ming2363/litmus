"""把多段预约收成一份合并后的占用表。"""

from typing import List, Sequence, Tuple

from booking.merge import merge_intervals


class BookingCalendar:
    """记录原始预约，读取时再合并。"""

    def __init__(self) -> None:
        self._pairs: List[Tuple[int, int]] = []

    @classmethod
    def from_pairs(cls, pairs: Sequence[Sequence[int]]) -> "BookingCalendar":
        calendar = cls()
        for pair in pairs:
            if isinstance(pair, (str, bytes)) or not isinstance(pair, Sequence) or len(pair) != 2:
                raise ValueError("每个区间必须有两个端点")
            calendar.add(pair[0], pair[1])
        return calendar

    def add(self, start: int, end: int) -> None:
        # 先走一遍合并校验，拒绝非法端点。
        merge_intervals([(start, end)])
        self._pairs.append((start, end))

    def ranges(self) -> List[Tuple[int, int]]:
        return merge_intervals(self._pairs)

    def raw_count(self) -> int:
        return len(self._pairs)
