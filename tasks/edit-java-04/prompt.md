# edit-java-04: 缩小 synchronized 临界区并保证并发线程安全

## 背景与需求

当前项目位于 `src/com/litmus/signing/`，实现了一个带容量上限（LRU 淘汰）、TTL 过期、主动吊销（`invalidateClient`）与统计指标（`MetricsSnapshot`）的令牌签发代理 `TokenBroker`。相关类包括：

- `SignedToken.java`：不可变令牌对象；
- `UpstreamSigner.java`：上游慢签名服务接口；
- `MetricsSnapshot.java`：不可变指标快照（`totalRequests`、`cacheHits`、`upstreamSignCalls`、`evictions`、`revocations`、`cacheSize`）；
- `TokenBroker.java`：令牌缓存与并发调度核心类。

目前 `TokenBroker` 将所有公开方法（`issueToken`、`invalidateClient`、`purgeExpired`、`snapshotMetrics`）粗暴地加上了方法级 `synchronized`，导致高耗时外部调用 `signer.sign(...)` 全程持有全局监视器锁，引发严重的并发吞吐阻塞。

请仅修改 `src/com/litmus/signing/TokenBroker.java`，将 `synchronized` 精确缩小到真正保护共享内存状态的临界区，并满足以下全部并发安全与业务不变量要求：

1. **外部签名 I/O 不持有锁（零串行阻塞）**：
   - 调用 `UpstreamSigner.sign(...)` 期间不得持有阻塞其他线程的锁。
   - 不同 `clientId` 的未命中请求必须能真正并发进入 `signer.sign(...)`，互相之间不得串行阻塞。
   - 当某个慢客户端请求阻塞在 `signer.sign(...)` 内部时，其他客户端的缓存命中读取、`snapshotMetrics()`、`purgeExpired(...)` 以及 `invalidateClient(...)`（包括针对同一 `clientId` 或其他 `clientId`）都必须立即执行并返回，不得卡死等待在途签名完成。
2. **并发吊销与乱序写回防护**：
   - 若在某 `clientId` 的 `issueToken` 正在上游签名期间发生 `invalidateClient(clientId)`，该笔在途旧签名完成后**不得**将失效前发起的旧令牌写入缓存，确保之后的 `issueToken` 请求重新签发有效新令牌。
   - 若同一 `clientId` 存在多笔并发签名因网络抖动乱序返回，过期时间更早（`expiresAtEpochMs` 更小或等于）的旧结果不得覆盖缓存中已存在的较新未过期令牌。
3. **指标守恒与缓存容量安全**：
   - 保持 `cache` 的 LRU 容量上限语义（缓存条目数任何时刻不得超过 `maxEntries`；仅容量超限逐出最久未使用条目时累计 `evictions`）。
   - 在并发读写、清理、吊销交织的情况下保持线程安全：所有共享状态与统计计数更新需原子一致，多线程结束后在静默状态下严格满足 `totalRequests == cacheHits + upstreamSignCalls`，`cacheSize` 与实际缓存条目一致。
   - 保持 `TokenBroker` 构造器与全部公开方法签名及参数校验（`IllegalArgumentException` 等）完全不变。

## 约束条件

- 只允许修改 `src/com/litmus/signing/TokenBroker.java`。
- **改动行数上限 (`max_changed_lines`)：`75` 行**。
- 不得修改 `SignedToken.java`、`UpstreamSigner.java`、`MetricsSnapshot.java` 或可见测试文件 `TokenBrokerPublicTest.java`。
- 仅使用 JDK 17 标准库，无第三方依赖；全部文件 UTF-8 编码、LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
