# edit-java-04: 把令牌签发的锁缩小到真正的临界区

## 背景

`TokenBroker` 给北港单证签发可缓存的令牌。现在的 `issueToken` 在调用 `signer.sign` 时一直占着 `lock`，别的签发、`invalidate` 和 `snapshot` 都会被堵住。请只改 `src/com/litmus/signing/TokenBroker.java`，把锁缩小到真正要保护的状态上。签名期间必须允许其他线程进入 `signer.sign`，也必须允许 `invalidate` 和 `snapshot` 返回。

改动行数不超过 18 行（统一换行并去掉行尾空白后，按差异的较大一侧计）。可见测试不能改。`issueTokenLegacy`、费率、审计环和说明方法都不要动，行数预算不够同时改它们。

## 行为

构造 `TokenBroker(Signer signer, Clock clock, int maxEntries)`。`signer` 或 `clock` 为 null 时抛出 `NullPointerException`。`maxEntries < 1` 时抛出 `IllegalArgumentException`。

`issueToken(clientId, subject, ttlMillis)`：

- `clientId`、`subject` 为 null，或去掉首尾空白后为空，抛出 `IllegalArgumentException`
- `ttlMillis <= 0` 抛出 `IllegalArgumentException`
- 非法参数不增加任何计数，也不调用签名器
- 缓存键同时包含 `clientId` 和 `subject`
- 到期时刻 `expiresAt = clock.now() + ttlMillis`，在进入 `signer.sign` 之前就确定，签名期间时钟再变化也不改这次的值
- 待签字节是 UTF-8 的 `clientId + "\n" + subject + "\n" + expiresAt` 的十进制文本。`Token.signature` 保存签名器返回字节的副本
- 未过期的缓存命中不再调用签名器，并返回缓存里的那枚令牌。`expiresAt <= clock.now()` 视为过期，从缓存移除，且 **不** 增加 `evictionCount`
- 容量淘汰使用访问顺序：命中会变成最近使用。超过 `maxEntries` 时移除最久未使用的一条，`evictionCount` 只在这种移除时加 1
- `totalRequests` 在签名之前、持有 `lock` 时加 1。`cacheHits` 在命中时加 1。`upstreamSignCalls` 在签名返回之后、再次持有 `lock` 时加 1。因此签名进行中的 `snapshot` 能看到 `totalRequests` 已增加、`upstreamSignCalls` 仍是旧值
- 成功调用始终满足 `totalRequests == cacheHits + upstreamSignCalls`
- 初始 `epoch` 是 0

发布规则（已有的 `publishIfCurrent` 就是这个语义，继续用它）：

- 进入签名前记下当时的 `epoch`。签名返回后如果 `epoch` 已经变了，返回刚签出的令牌，但不写入缓存
- 若缓存里已有未过期、且 `expiresAt` 更大或相等的令牌，保留缓存中的那一条。这次调用仍返回自己刚签出的令牌
- 否则写入刚签出的令牌并返回它
- 两个键相同的 `issueToken` 若都在对方发布前通过了缓存查找，就必须各自签名一次，再按上面的到期时刻规则收口

`invalidate()` 把 `epoch` 加 1 并清空缓存，不重置计数器。即使有签名正在进行，它也要在 500 毫秒内返回。

`snapshot()` 返回计数器、缓存条数和 `epoch` 的副本。即使有签名正在进行，也要在 500 毫秒内返回。

`lookup` 返回未过期令牌，过期则返回 null 并移除。

锁继续使用现有的 `lock` 对象。不要把 `signer.sign` 放进这个锁里。

## 如何自测

在仓库根执行 `python3 litmus.py check`。可见测试用标准库风格的 `public void test*()`，失败抛出 `AssertionError`。
