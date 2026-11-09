"""岸桥保养工单。工单占用的是机时，不写进巷道账本。"""

from typing import Dict, List, Optional, Sequence, Tuple

Job = Tuple[str, int, int, str]  # 工单号, 开始分钟, 结束分钟, 岸桥


class WorkOrderBook:
    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}

    def add(self, job_id: str, start: int, end: int, crane_id: str) -> None:
        if not job_id or not crane_id:
            raise ValueError("工单号和岸桥不能为空")
        if type(start) is not int or type(end) is not int or start >= end:
            raise ValueError("保养区间不合法")
        if job_id in self._jobs:
            raise ValueError("工单重复")
        self._jobs[job_id] = (job_id, start, end, crane_id)

    def cancel(self, job_id: str) -> None:
        if job_id not in self._jobs:
            raise KeyError(job_id)
        del self._jobs[job_id]

    def on_crane(self, crane_id: str) -> List[Job]:
        rows = [job for job in self._jobs.values() if job[3] == crane_id]
        rows.sort(key=lambda job: (job[1], job[0]))
        return rows

    def conflicts(self, crane_id: str) -> List[Tuple[str, str]]:
        rows = self.on_crane(crane_id)
        found = []
        for index in range(len(rows)):
            for other in range(index + 1, len(rows)):
                if rows[other][1] < rows[index][2]:
                    found.append((rows[index][0], rows[other][0]))
                else:
                    break
        return found

    def busy_minutes(self, crane_id: str, start: int, end: int) -> int:
        if start >= end:
            raise ValueError("查询区间不合法")
        total = 0
        for _job_id, job_start, job_end, _crane in self.on_crane(crane_id):
            left = max(start, job_start)
            right = min(end, job_end)
            if left < right:
                total += right - left
        return total

    def free_gaps(self, crane_id: str, start: int, end: int) -> List[Tuple[int, int]]:
        """查询区间里没被保养占住的半开段。"""
        if start >= end:
            raise ValueError("查询区间不合法")
        cursor = start
        gaps = []
        for _job_id, job_start, job_end, _crane in self.on_crane(crane_id):
            if job_end <= start or job_start >= end:
                continue
            if job_start > cursor:
                gaps.append((cursor, min(job_start, end)))
            cursor = max(cursor, job_end)
            if cursor >= end:
                break
        if cursor < end:
            gaps.append((cursor, end))
        return gaps


PARTS = {
    "钢丝绳": 4,
    "滑轮": 8,
    "制动片": 2,
    "电控模块": 1,
}

HOURS = {
    "钢丝绳": 180,
    "滑轮": 90,
    "制动片": 60,
    "电控模块": 240,
}


def labour_minutes(parts: Sequence[Tuple[str, int]]) -> int:
    total = 0
    for name, count in parts:
        if name not in HOURS:
            raise ValueError("未知配件")
        if type(count) is not int or count <= 0:
            raise ValueError("配件数量不合法")
        total += HOURS[name] * count
    return total


def within_stock(parts: Sequence[Tuple[str, int]]) -> bool:
    for name, count in parts:
        if name not in PARTS or count > PARTS[name]:
            return False
    return True


def suggest_window(book: WorkOrderBook, crane_id: str, duration: int, horizon: Tuple[int, int]) -> Optional[Tuple[int, int]]:
    """在视野里找第一段能放下这次保养的空隙。"""
    if duration <= 0:
        raise ValueError("保养时长必须为正")
    start, end = horizon
    for gap_start, gap_end in book.free_gaps(crane_id, start, end):
        if gap_end - gap_start >= duration:
            return (gap_start, gap_start + duration)
    return None
