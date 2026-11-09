"""从一段占用上挖掉封控。"""

from typing import List, Sequence, Tuple

Span = Tuple[int, int]


class BlockClip:
    """按封控列表逐段挖除。"""

    def punch(self, window: Span, blocks: Sequence[Span]) -> List[Span]:
        segments: List[Span] = [window]
        for block_start, block_end in blocks:
            nxt: List[Span] = []
            for left, right in segments:
                if block_end < left or block_start >= right:
                    nxt.append((left, right))
                    continue
                if left < block_start:
                    nxt.append((left, block_start))
                if block_end + 1 < right:
                    nxt.append((block_end + 1, right))
            segments = [seg for seg in nxt if seg[0] < seg[1]]
        return segments
