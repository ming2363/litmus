"""把调度台录入折成账本内部的占用和封控。"""

from typing import Tuple

Hold = Tuple[int, int, str]
Block = Tuple[int, int]


class Normalizer:
    """校验一批录入。"""

    def minute(self, value: object) -> int:
        if not isinstance(value, int):
            raise ValueError("分钟编号必须是整数")
        return value

    def lane_code(self, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("巷道编号必须是文本")
        text = value.strip()
        if not text:
            raise ValueError("巷道编号不能为空")
        return text

    def hold(self, item: object) -> Hold:
        if not isinstance(item, tuple) or len(item) != 3:
            raise ValueError("占用必须是长度为 3 的元组")
        start = self.minute(item[0])
        end = self.minute(item[1])
        if start >= end:
            raise ValueError("占用区间必须满足 start < end")
        return (start, end, self.lane_code(item[2]))

    def block(self, item: object) -> Block:
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("封控必须是长度为 2 的元组")
        start = self.minute(item[0])
        end = self.minute(item[1])
        if start >= end:
            raise ValueError("封控区间必须满足 start < end")
        return (start, end)
