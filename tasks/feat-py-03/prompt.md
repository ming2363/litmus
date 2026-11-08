# feat-py-03: 仓储路径规划第二阶段（带权能耗与批量寻路）

## 背景与需求

当前仓库是仓储 AGV 机器人栅格路径规划模块（`src/planner.py`）。

第一阶段已经实现并可通过可见测试：
- `parse_grid(lines: Sequence[str]) -> List[str]`：校验非空矩形栅格，仅允许字符 `#`（障碍货架）、`.`（普通通道）以及 `'1'`～`'9'`。
- `find_min_steps(grid: Sequence[str], start: Coord, goal: Coord) -> Optional[int]`：无权重、无转向代价的 4 邻域最短步数（`.` 与 `'1'`～`'9'` 均视为可通过且每步代价为 1）。

现在需求升级为**第二阶段**：不同通道地面具有不同能耗权重，AGV 转弯需要额外耗时/能耗，且需要一次批量计算从任意充电站集合到上千个拣货目标点的最小能耗：

请在 `src/planner.py` 中保持第一阶段函数签名与行为完全不变的同时，新增实现以下两个函数：

1. `find_min_energy_batch(grid: Sequence[str], starts: Sequence[Coord], goals: Sequence[Coord], turn_cost: int = 0) -> Dict[Coord, Optional[int]]`
2. `find_min_energy(grid: Sequence[str], start: Coord, goal: Coord, turn_cost: int = 0) -> Optional[int]`

### 详细规则

1. **单元格进入能耗**：
   - `'#'`：不可通行障碍。
   - `'.'`：进入该格消耗 `1` 单位能耗。
   - `'1'`～`'9'`：进入该格消耗 `int(ch)` 单位能耗。
   - 起点本身不计入进入能耗（即从起点出发时的初始累计能耗为 `0`；若某合法非 `'#'` 坐标既是起点又是目标，其最小能耗为 `0`）。
2. **移动与转向代价**：
   - 允许上下左右 4 邻域移动（不能越界或进入 `'#'`）。
   - 起步第一步可朝任意方向出发，**不产生转向代价**；此后每当当前移动方向与上一步移动方向不同（包括 90° 转弯或 180° 掉头），额外增加 `turn_cost` 单位能耗。
   - `turn_cost` 必须为非负整数（`turn_cost < 0` 或非整数/`bool` 时抛出 `ValueError`）。
3. **批量与多源语义**：
   - `find_min_energy_batch` 计算从 `starts` 中**任意一个可通行起点**出发到达 `goals` 中每个目标坐标的最小总能耗，返回字典 `{goal_coord: min_energy_or_None}`。
   - 若 `goals` 中某坐标为 `'#'` 或不可达，对应值为 `None`。
   - 若 `goals` 为空，返回 `{}`。
4. **参数校验**：
   - `grid` 格式非法、或 `starts` 为空、或 `starts` / `goals` 中任意坐标 `(r, c)` 越界，必须抛出 `ValueError`。
   - 若 `starts` 中某个坐标恰好是 `'#'`，该起点无法出发；若全部起点都是 `'#'`，所有目标返回 `None`（对于 `find_min_energy`，若 `start` 或 `goal` 为 `'#'` 返回 `None`）。
5. **性能要求**：
   - 隐藏测试包含 `200 × 200` 规模网格与上千个 `goals` 的批量查询。要求使用高效的最短路算法（如基于 `heapq` 的单次多源 Dijkstra 状态搜索），在 1 秒内完成，禁止对每个目标重复跑一次寻路。

## 约束条件

- 只允许修改 `src/*.py` 范围内的文件。
- 不得修改或删除可见测试文件 `tests/test_public.py`。
- 仅使用 Python 标准库（兼容 Python 3.9～3.14），UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
