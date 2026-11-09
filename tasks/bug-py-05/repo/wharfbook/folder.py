"""同一巷道内的占用折叠。

相接的两段留出交接缝。
"""

from typing import List, Sequence, Tuple

Span = Tuple[int, int]


class LaneFolder:
    """按录入顺序把一段段占用收进结果。"""

    def fold(self, spans: Sequence[Span]) -> List[Span]:
        result: List[Span] = []
        for start, end in spans:
            absorbed = False
            for index, (kept_start, kept_end) in enumerate(result):
                if start < kept_end and end > kept_start:
                    result[index] = (min(kept_start, start), end)
                    absorbed = True
                    break
            if not absorbed:
                result.append((start, end))
            result.sort(key=lambda item: (item[0], item[1]))
        return result
