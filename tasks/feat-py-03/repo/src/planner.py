"""仓储 AGV 路径规划模块（第一阶段已完成，第二阶段待实现）。"""

from collections import deque
from typing import Dict, List, Optional, Sequence, Tuple

Coord = Tuple[int, int]

_VALID_CELLS = set("#.123456789")
_DIRS: Tuple[Coord, ...] = ((-1, 0), (0, 1), (1, 0), (0, -1))


def parse_grid(lines: Sequence[str]) -> List[str]:
    """校验并规范化矩形栅格地图。"""
    if not lines:
        raise ValueError("地图不能为空")
    rows = [str(line) for line in lines]
    width = len(rows[0])
    if width == 0:
        raise ValueError("地图行宽不能为 0")
    for idx, row in enumerate(rows):
        if len(row) != width:
            raise ValueError("第 {} 行长度不一致: {} != {}".format(idx, len(row), width))
        for ch in row:
            if ch not in _VALID_CELLS:
                raise ValueError("包含非法地图字符: {!r}".format(ch))
    return rows


def _validate_coord(coord: Coord, rows: int, cols: int, label: str) -> Coord:
    if not isinstance(coord, tuple) or len(coord) != 2:
        raise ValueError("{} 坐标格式非法: {!r}".format(label, coord))
    r, c = coord
    if isinstance(r, bool) or isinstance(c, bool) or not isinstance(r, int) or not isinstance(c, int):
        raise ValueError("{} 坐标必须是整数二元组: {!r}".format(label, coord))
    if r < 0 or r >= rows or c < 0 or c >= cols:
        raise ValueError("{} 坐标越界: {!r}".format(label, coord))
    return (r, c)


def find_min_steps(grid: Sequence[str], start: Coord, goal: Coord) -> Optional[int]:
    """第一阶段：计算无权重、无转向代价的 4 邻域最少步数。"""
    rows = parse_grid(grid)
    height = len(rows)
    width = len(rows[0])
    sr, sc = _validate_coord(start, height, width, "start")
    gr, gc = _validate_coord(goal, height, width, "goal")

    if rows[sr][sc] == "#" or rows[gr][gc] == "#":
        return None
    if (sr, sc) == (gr, gc):
        return 0

    visited = {(sr, sc)}
    queue = deque([(sr, sc, 0)])
    while queue:
        r, c, steps = queue.popleft()
        for dr, dc in _DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < height and 0 <= nc < width and rows[nr][nc] != "#":
                if (nr, nc) == (gr, gc):
                    return steps + 1
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc, steps + 1))
    return None


def find_min_energy_batch(
    grid: Sequence[str],
    starts: Sequence[Coord],
    goals: Sequence[Coord],
    turn_cost: int = 0,
) -> Dict[Coord, Optional[int]]:
    """第二阶段：批量计算多起点到多目标的最小能耗（含单元格权重与转向代价）。"""
    raise NotImplementedError("find_min_energy_batch 尚未实现")


def find_min_energy(
    grid: Sequence[str],
    start: Coord,
    goal: Coord,
    turn_cost: int = 0,
) -> Optional[int]:
    """第二阶段：计算单起点到单目标的最小能耗。"""
    raise NotImplementedError("find_min_energy 尚未实现")
