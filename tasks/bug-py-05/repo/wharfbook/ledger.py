"""码头巷道占用账本的对外入口。"""

from typing import List, Sequence, Tuple

from wharfbook.planner import Planner

Hold = Tuple[int, int, str]
Block = Tuple[int, int]


class WharfLedger:
    """一次计划提交。"""

    def __init__(self) -> None:
        self.planner = Planner()

    def plan(self, holds: Sequence[Hold], blocks: Sequence[Block]) -> List[Hold]:
        """返回这批占用在封控之后的巷道计划。"""
        return self.planner.compose(holds, blocks)
