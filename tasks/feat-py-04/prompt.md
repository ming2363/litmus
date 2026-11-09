# 并发安全的潮汐令牌桶

闸口要按键发放潮汐令牌。原型能校验参数，但 `try_acquire` 还不会真正扣减，多把锁也还没分开。请在 `src/` 里实现下面的全部规则。`src/legacy_gate.py` 是一份没有冻结、也没有按键分锁的旧草稿，不能把它的行为当成现行规则。

## 已有类型

`Clock.now()` 返回秒，类型是 `float`。未传入时钟时，`TokenLimiter` 使用 `MonotonicClock`。测试会传入 `ManualClock`：`advance` 只接受非负的 `int` 或 `float`，`set` 接受有限的 `int` 或 `float`。`bool` 一律非法。

`RateLimitPolicy(capacity, rate, freeze_after=None, burst=None)`：

- `capacity` 必须是 `int` 且不能是 `bool`，并且 `>= 1`。
- `rate` 必须是有限的 `int` 或 `float`，不能是 `bool`，并且 `>= 0`。保存为 `float`。
- `freeze_after` 为 `None` 表示不冻结。否则必须是有限的、`>= 0` 的 `int` 或 `float`，不能是 `bool`，保存为 `float`。
- `burst` 为 `None` 时忽略。传入时必须是 `int`、不能是 `bool`，并且等于 `capacity`，否则 `ValueError`。
- 非法参数抛出 `ValueError`。

`BucketStats` 至少包含这些属性：`tokens`、`capacity`、`rate`、`freeze_after`、`allowed_requests`、`allowed_tokens`、`rejected_requests`、`last_active`、`waiters`。`tokens`、`rate`、`freeze_after`、`last_active` 用数值比较时允许绝对误差 `1e-9`。`freeze_after` 不冻结时为 `None`。

## 键、数量和超时

- 键必须是非空 `str`。不去掉首尾空白，`" a "` 和 `"a"` 是两把不同的桶。非法键抛出 `ValueError`。
- `tokens` 必须是 `int` 且不能是 `bool`，并且 `1 <= tokens <= 当时策略的 capacity`。不满足就抛出 `ValueError`。这个检查发生在扣减之前；因此失败时不创建桶、不改计数、不改 `last_active`。
- `try_acquire` 和 `acquire` 进入桶锁之后，要按锁内的当前 `capacity` 再查一次。策略若已变小，请求超过新容量时抛出 `ValueError`，同样不记拒绝、不改 `last_active`。
- `acquire` 的 `timeout` 为 `None` 表示一直等到规则允许停止。否则必须是有限的、`>= 0` 的 `int` 或 `float`，不能是 `bool`。`0` 表示不等待。
- `timeout` 按真实经过的时间（`time.monotonic()`）计算，与注入的时钟无关；补充令牌仍然只看注入的时钟。测试里的 `ManualClock` 在等待期间不会前进。

## 建桶和补充

每个键第一次进入 `try_acquire` 或 `acquire` 时才建桶。`update_policy` 对还没有桶的键只记录待用策略，`stats` 仍返回 `None`，`prune_idle` 也不把它算进桶。同一键多次预置时，后一次覆盖前一次。建桶时采用待用策略，没有则用构造时的默认策略。初始令牌等于 `capacity`，`last_refill` 和 `last_active` 都是建桶时的 `clock.now()`。

补充令牌时：

- `now < last_refill` 视为时钟回拨：不加令牌。`try_acquire`、`acquire` 和 `update_policy` 把 `last_refill` 改到 `now`。`stats` 遇到回拨不改 `last_refill`。
- 没有冻结时，经过的时间是 `max(0, now - last_refill)`，令牌增加 `经过时间 * rate`，再封顶到 `capacity`。会改变桶的调用把 `last_refill` 设为 `now`。
- `freeze_after` 不是 `None` 时，冻结时刻是 `last_active + freeze_after`。只补充 `last_refill` 到 `min(now, 冻结时刻)` 这一段；`last_refill` 已经不早于冻结时刻时，补充量为 0。闲置更久也不会把令牌补满。
- `try_acquire`、`acquire`、`update_policy` 在按上面的规则补充之后，把 `last_refill` 设为 `now`，闲置段被丢掉，以后从这次调用重新开始补充。
- `stats` 补充到冻结时刻为止，把 `last_refill` 停在已经补充过的位置，不跳到 `now`，也不修改 `last_active`。

判断够不够扣时，用 `tokens + 1e-9 >= 请求量`。扣减后的令牌不能小于 0。

## 获取

`try_acquire(key, tokens=1)` 不阻塞。够则扣减，`allowed_requests += 1`，`allowed_tokens += tokens`，返回 `True`。不够则不扣减，`rejected_requests += 1`，返回 `False`。成功和拒绝都把 `last_active` 更新为当前时钟。校验失败不更新。

`acquire(key, tokens=1, timeout=None)` 使用同一套补充和扣减。需要等待时只等待这一把桶，不能占着会挡住其他键的锁。其他键上的 `try_acquire`、`acquire`、`stats`、`update_policy`、`prune_idle` 必须能同时进行。

等待规则：

- 当前令牌不够、`rate == 0` 且 `timeout is None`：抛出 `ValueError`，不改计数和 `last_active`。
- `timeout` 用尽仍不够：`rejected_requests += 1`，`last_active` 更新为本次尝试的时钟，返回 `False`。
- 等待被 `update_policy` 唤醒后，按新策略重新补充和校验。新 `capacity` 小于请求量时抛出 `ValueError`，不记拒绝。
- 等待期间 `waiters` 至少为 1，结束后恢复。`stats` 能看到等待中的 `waiters`。

`rate == 0` 时令牌不会随时间增加。`timeout == 0` 且当前不够时立刻返回 `False`。

## 策略、清理和统计

`update_policy(key, policy)`：`policy` 不是 `RateLimitPolicy` 时抛出 `TypeError`。对已有的桶，先按旧策略结算到当前时钟（含冻结和回拨），再换上新策略；令牌超过新 `capacity` 时截断到新 `capacity`。然后唤醒这把桶上的等待者。`update_policy` 不修改 `last_active`。

`prune_idle(max_idle_seconds)`：参数必须是有限的、`>= 0` 的 `int` 或 `float`，不能是 `bool`，否则 `ValueError`。删除 `waiters == 0` 且 `now - last_active >= max_idle_seconds` 的桶，返回删除个数。有等待者的桶留着。清理本身不修改留存桶的 `last_active`。

`stats(key)` 对没有桶的键返回 `None`。有桶时先按 `stats` 的补充规则结算，再返回快照。`all_stats()` 返回 `{键: 快照}`，不包含只有预置策略、尚未建桶的键。

16 个线程同时对同一把桶调用 `try_acquire` 时，成功扣掉的令牌总数不能超过结算后的可用量，也不能把同一次成功算丢。不同键的等待不能互相堵住。

## 约束

只修改 `src/*.py`。不要改测试。只用 Python 标准库，兼容 3.9 到 3.14。

## 如何自测

`python3 litmus.py check`
