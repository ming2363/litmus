# feat-py-04: 并发安全的令牌桶限流器

## 背景与需求

当前仓库是一个多租户 API 网关限流组件，目录包含：
- `src/clock.py`：时钟抽象（`Clock`、`MonotonicClock`、`ManualClock`）
- `src/models.py`：策略与统计快照模型（`RateLimitPolicy`、`BucketStats`）
- `src/bucket.py`：单键令牌桶状态（当前原型缺少并发安全控制与精确边界处理）
- `src/limiter.py`：多键限流器入口 `TokenLimiter`（`acquire`、`update_policy`、`prune_idle` 等尚未完成，且当前 `try_acquire` 在多线程竞争下不安全）

请你完善 `src/bucket.py` 与 `src/limiter.py`（必要时可调整配合模块），实现一个高并发安全、隔离性良好且统计精确的令牌桶限流器 `TokenLimiter`。

### 精确接口与行为要求

1. **构造与策略**：
   - `TokenLimiter(default_policy: RateLimitPolicy, clock: Optional[Clock] = None)`：若未传 `clock`，默认使用 `MonotonicClock()`。
   - 每个 `key` 首次出现时按当前 `default_policy`（或已通过 `update_policy` 配置的策略）初始化令牌桶，初始令牌数等于策略的 `capacity`。
   - 所有接口对 `key` 校验：必须为非空字符串（`isinstance(key, str) and len(key) > 0`），否则抛出 `ValueError`。
   - 所有获取接口对 `tokens` 校验：必须是整数（非 `bool`）且 `1 <= tokens <= policy.capacity`，否则抛出 `ValueError`（包括 `tokens > capacity` 时必须立即抛出 `ValueError`，不得永久阻塞或静默返回 `False`）。

2. **非阻塞获取 `try_acquire(key: str, tokens: int = 1) -> bool`**：
   - 使用 `clock.now()` 计算自上次补充以来经过的时间 `elapsed = max(0.0, now - last_refill)`，按 `elapsed * rate` 补充令牌并封顶至 `capacity`。
   - 考虑到浮点运算累积误差，判断余量时使用微小容差（例如 `1e-12`）以避免刚好凑够整数令牌时误判不足，扣减后余量不小于 `0.0`。
   - 令牌足够则原子扣减，累加 `allowed_requests += 1` 与 `allowed_tokens += tokens`，返回 `True`；不足则不扣减，累加 `rejected_requests += 1`，返回 `False`。
   - **并发要求**：在 16 线程通过 `Barrier` 并发争抢同一 `key` 时，放行总令牌数绝不能超发，也不能丢失扣减或统计计数。

3. **阻塞等待获取 `acquire(key: str, tokens: int = 1, timeout: Optional[float] = None) -> bool`**：
   - `timeout` 若不为 `None`，必须为有限非负数（非 `bool`），否则抛出 `ValueError`。
   - 若桶内当前令牌不足且 `policy.rate == 0.0` 且 `timeout is None`，应抛出 `ValueError`（防止无限死锁）；若 `timeout is not None`，等待至超时后返回 `False` 并计入 `rejected_requests`。
   - **细粒度锁与跨键隔离要求**：等待令牌期间**绝不能持有全局锁或阻塞其他 `key`**；当 `key="A"` 在 `acquire` 中阻塞等待时，另一线程对 `key="B"` 调用 `try_acquire`、`acquire`、`stats` 或 `update_policy` 必须能立即执行而不被阻塞。
   - 使用 `Condition` 等待令牌补充并在超时前不断按实际剩余时间重试，超时仍不足时计入 `rejected_requests += 1` 并返回 `False`。

4. **动态策略更新 `update_policy(key: str, policy: RateLimitPolicy) -> None`**：
   - `policy` 必须为 `RateLimitPolicy` 实例（否则抛出 `TypeError` 或 `ValueError`）。
   - 更新该 `key` 的策略（若该 `key` 尚未创建，则按新策略预创建桶或记录策略，后续新建桶使用新策略）。
   - 对已存在的桶先按旧速率结算到当前时刻，再应用新策略：若新 `capacity` 小于当前已有 `tokens`，将 `tokens` 截断到新 `capacity`；同时唤醒正在等待该桶的 `acquire` 线程以按新策略重新计算等待时间（若新 `capacity` 已经小于等待线程请求的 `tokens`，等待线程应抛出 `ValueError` 或及时结束等待）。

5. **闲置桶清理 `prune_idle(max_idle_seconds: float) -> int`**：
   - `max_idle_seconds` 必须为有限非负数（非 `bool`），否则抛出 `ValueError`。
   - 清理满足 `now - last_active >= max_idle_seconds` **且当前没有等待线程 (`waiters == 0`)** 的桶，返回清理掉的桶数量。
   - 在多线程同时执行 `try_acquire` / `acquire` / `stats` / `prune_idle` 时，不得出现字典迭代修改异常（`RuntimeError`）或误删正在等待中的桶。

6. **统计快照 `stats(key: str) -> Optional[BucketStats]` 与 `all_stats() -> Dict[str, BucketStats]`**：
   - `stats(key)` 若 `key` 不存在返回 `None`；存在则先按当前时钟惰性补充（但不算作请求也不刷新 `last_active`），返回最新的 `BucketStats` 快照。
   - `all_stats()` 返回当前所有桶的 `{key: BucketStats}` 一致快照。

## 约束条件

- 只允许修改 `src/*.py` 范围内的文件。
- 不得修改或删除可见测试文件 `tests/test_public.py`。
- 仅使用 Python 标准库（兼容 Python 3.9～3.14），UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
