"""导出前排列抄表。"""

from typing import List, Sequence

from protocol.reading import Reading


def sort_readings(rows: Sequence[Reading]) -> List[Reading]:
    return sorted(rows, key=lambda item: (item.taken_at, item.meter_id), reverse=True)
