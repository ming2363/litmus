"""把占用、封控组织成一版巷道计划。"""

from typing import Dict, List, Sequence, Tuple

from wharfbook.clip import BlockClip
from wharfbook.folder import LaneFolder
from wharfbook.normalize import Normalizer

Hold = Tuple[int, int, str]
Block = Tuple[int, int]


class Planner:
    """调度台一次重排的编排。"""

    def __init__(self) -> None:
        self.normalizer = Normalizer()
        self.folder = LaneFolder()
        self.clip = BlockClip()

    def compose(self, holds: Sequence[Hold], blocks: Sequence[Block]) -> List[Hold]:
        if not holds:
            return []
        if isinstance(holds, list) and all(
            isinstance(item, tuple) and len(item) == 3 for item in holds
        ):
            holds.sort(key=lambda item: (str(item[2]), item[0], item[1]))
        if isinstance(blocks, list) and all(
            isinstance(item, tuple) and len(item) == 2 for item in blocks
        ):
            blocks.sort()
        clean_holds = [self.normalizer.hold(item) for item in holds]
        clean_blocks = [self.normalizer.block(item) for item in blocks]
        grouped: Dict[str, List[Block]] = {}
        for start, end, lane in clean_holds:
            grouped.setdefault(lane, []).append((start, end))
        planned: List[Hold] = []
        for lane, spans in grouped.items():
            for start, end in self.folder.fold(spans):
                for kept_start, kept_end in self.clip.punch((start, end), clean_blocks):
                    planned.append((kept_start, kept_end, lane))
        return planned
