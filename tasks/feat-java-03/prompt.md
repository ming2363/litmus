# feat-java-03: 旋转正多边形内小球碰撞反弹物理步进

## 背景与需求

当前仓库是一个无图形界面的二维刚体物理步进核心模块（包名 `com.litmus.physics`），用于模拟一个小球在绕原点旋转的正多边形容器内部的运动与弹性碰撞。已有类如下：
- `Vec2.java`：二维不可变向量及点乘、长度、归一化等辅助方法。
- `PolygonConfig.java`：正多边形与物理参数配置（边数 `sides`、外接圆半径 `circumradius`、角速度 `omega`、重力加速度 `gravity`、恢复系数 `restitution`、小球半径 `ballRadius`），以及内切圆半径 `apothem()`。
- `BallState.java`：状态快照（`x, y, vx, vy, theta`）。
- `Simulation.java`：模拟主类，已实现 `getState()`、`getConfig()`、`getVertices()`、`minEdgeClearance()`、`isInside()` 等几何查询方法，但 `step(double dt)` 尚未实现。

请你完善 `src/com/litmus/physics/Simulation.java` 中的 `public void step(double dt)` 方法。

### 精确物理与几何规范

1. **坐标系与正多边形定义**：
   - 使用右手直角坐标系，原点 `(0, 0)` 为多边形旋转中心，`+y` 方向朝上，重力加速度方向为 `(0, -gravity)`。
   - 多边形当前旋转角为 `theta`（逆时针为正，角速度为 `omega` 弧度/秒）。
   - 第 `k` 个顶点（`k = 0 .. sides - 1`）的坐标为：
     `(R * cos(theta + 2πk / sides), R * sin(theta + 2πk / sides))`。
   - 第 `k` 条边（连接顶点 `k` 与 `(k + 1) % sides`）对应的外向单位法线角为 `midAngle = theta + π * (2k + 1) / sides`，外向单位法线 `u_k = (cos(midAngle), sin(midAngle))`，内向单位法线 `n_k = -u_k`。
   - 球心 `(x, y)` 相对于第 `k` 条边的有效内向余量为：
     `clearance_k = apothem - (x * u_k.x + y * u_k.y) - ballRadius`。
     其中 `apothem = circumradius * cos(π / sides)`。当所有边满足 `clearance_k >= 0` 时小球完全位于容器内部。

2. **参数校验与子步积分**：
   - 若 `!Double.isFinite(dt) || dt < 0.0`，抛出 `IllegalArgumentException`。若 `dt == 0.0`，状态保持不变直接返回。
   - 为保证高速运动与大时间步长下的碰撞稳定性，请采用小步长子步积分（每个子步 `h <= 0.0005` 秒，例如 `substeps = Math.max(1, (int) Math.ceil(dt / 0.0005))`，`h = dt / substeps`）。
   - 每个子步内按半隐式欧拉推进：
     - `theta += omega * h`
     - `vy -= gravity * h`
     - `x += vx * h`
     - `y += vy * h`
     - 随后检测并处理与多边形全部 `sides` 条边的碰撞穿透。

3. **旋转壁面碰撞与反弹**：
   - 当某条边满足 `clearance_k < 0`（穿透量 `penetration = -clearance_k > 0`）时：
     1. **位置拉回**：沿内向法线 `n_k` 推回容器内部：`x += penetration * n_k.x`，`y += penetration * n_k.y`（若同时穿透角落的多条边，可多轮迭代拉回直至不穿透任意边）。
     2. **计算壁面接触点速度**：接触点 `C = (x - ballRadius * n_k.x, y - ballRadius * n_k.y)`，由于容器绕原点以角速度 `omega` 旋转，该点壁面线速度为 `v_wall = (-omega * C.y, omega * C.x)`。
     3. **相对速度法向反射**：令相对速度 `v_rel = v - v_wall`，法向相对分量 `vn = dot(v_rel, n_k)`。仅当 `vn < 0`（小球相对壁面朝外运动）时按无摩擦弹性恢复系数 `e = restitution` 反弹：
        `vx -= (1.0 + e) * vn * n_k.x`
        `vy -= (1.0 + e) * vn * n_k.y`

## 约束条件

- 只允许修改 `src/**/*.java` 范围内的文件。
- 不得修改或删除可见测试文件 `src/com/litmus/physics/SimulationPublicTest.java`。
- 仅使用 JDK 17 标准库；全部文件 UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
