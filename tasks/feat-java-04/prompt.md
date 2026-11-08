# feat-java-04: 事件溯源聚合状态重建与快照机制

## 背景与需求

当前仓库是一个基于事件溯源（Event Sourcing）的仓储库存聚合模块（包名 `com.litmus.es`），包含以下 8 个核心文件：
- `EventType.java`：事件类型枚举（`STOCK_RECEIVED`、`STOCK_RESERVED`、`RESERVATION_RELEASED`、`STOCK_SHIPPED`）。
- `InventoryEvent.java`：不可变领域事件。
- `OptimisticConcurrencyException.java`：乐观并发冲突异常。
- `InventoryState.java`：聚合状态（`onHand`、`reserved`、`version`、`reservations`）。
- `EventStore.java` & `InMemoryEventStore.java`：事件日志存储接口与内存实现。
- `Snapshot.java` & `SnapshotStore.java` & `InMemorySnapshotStore.java`：快照模型、存储接口与内存实现。
- `InventoryRepository.java`：聚合仓储服务，负责命令处理、事件持久化、状态重建与快照管理。

当前起始代码仅实现了基础的入库（`receiveStock`）与预占（`reserveStock`）及全量重放，缺少乐观锁校验、释放/发货事件、快照保存与增量重建、历史版本回溯等关键能力。请你跨文件完善该模块：

### 1. 完善事件存储 `InMemoryEventStore.java`

- `append(String aggregateId, long expectedVersion, List<InventoryEvent> newEvents)`：
  - 校验参数合法性（`aggregateId` 非空、`newEvents` 非空且每个事件的 `aggregateId` 一致、`expectedVersion >= 0`），否则抛 `IllegalArgumentException`。
  - 校验乐观锁：若该聚合当前最新版本 `!= expectedVersion`，必须抛出 `OptimisticConcurrencyException`。
  - 校验事件序列号连续递增：第 `i` 个事件的 `sequence` 必须严格等于 `expectedVersion + 1 + i`，否则抛 `IllegalStateException`。
  - 支持线程安全的并发追加与读取（只读返回的列表不得被外部修改）。
- `readEventsAfter(String aggregateId, long fromVersionExclusive)`：按 `sequence` 升序返回 `sequence > fromVersionExclusive` 的事件。
- `readEventsRange(String aggregateId, long fromVersionExclusive, long toVersionInclusive)`：按 `sequence` 升序返回 `fromVersionExclusive < sequence <= toVersionInclusive` 的事件（若 `toVersionInclusive < fromVersionExclusive` 抛 `IllegalArgumentException`）。

### 2. 完善状态转移 `InventoryState.java`

- 保持不可变设计与深拷贝隔离：`getReservations()` 返回不可变视图，快照或外部引用绝不能被后续状态变更污染。
- `apply(InventoryEvent event)`：
  - 校验 `event.getAggregateId()` 匹配且 `event.getSequence() == version + 1`（序号不匹配抛 `IllegalStateException`，`aggregateId` 不匹配或数量 `<= 0` 抛 `IllegalArgumentException`）。
  - `STOCK_RECEIVED`：`onHand += quantity`。
  - `STOCK_RESERVED`：`referenceId` 非空且 `available() >= quantity`（否则抛 `IllegalStateException`），累加 `reserved` 及 `reservations` 中该 `referenceId` 的数量。
  - `RESERVATION_RELEASED`：`referenceId` 当前已预占量必须 `>= quantity`（否则抛 `IllegalStateException`），扣减 `reserved` 与该 `referenceId` 预占量；若该 `referenceId` 剩余预占为 `0`，从 `reservations` 映射中移除该键。
  - `STOCK_SHIPPED`：`referenceId` 当前已预占量必须 `>= quantity` 且 `onHand >= quantity`（否则抛 `IllegalStateException`），同时扣减 `onHand`、`reserved` 与该 `referenceId` 预占量；若剩余预占为 `0` 则从 `reservations` 中移除。

### 3. 实现内存快照存储 `InMemorySnapshotStore.java`

- `save(Snapshot snapshot)`：保存快照（`snapshot == null` 抛 `IllegalArgumentException`），保证已保存快照不受外部对象后续变更影响，按聚合保留历史快照（同版本号可覆盖更新）。
- `loadLatest(String aggregateId)`：返回该聚合版本号最大的快照；无快照返回 `Optional.empty()`。
- `loadLatestAtOrBefore(String aggregateId, long maxVersion)`：返回该聚合中满足 `version <= maxVersion` 的最大版本快照；无满足条件的快照返回 `Optional.empty()`。

### 4. 完善仓储服务 `InventoryRepository.java`

- **快照间隔保存**：构造参数 `snapshotInterval >= 0`（`< 0` 抛 `IllegalArgumentException`）。当 `snapshotInterval > 0` 时，每当推进产生的新状态版本号满足 `version > 0 && version % snapshotInterval == 0`，自动调用 `snapshotStore.save(...)` 保存该版本快照；`snapshotInterval == 0` 时不自动保存快照。
- **增量重建 `load(String aggregateId)`**：
  - 优先查询 `snapshotStore.loadLatest(aggregateId)`。
  - 若存在快照且 `snapshot.getVersion() <= eventStore.currentVersion(aggregateId)`，以该快照状态为起点，**仅调用 `eventStore.readEventsAfter(aggregateId, snapshot.getVersion())` 读取增量事件并重放**（不得全量重放快照之前的历史事件）。
  - 若不存在快照或快照版本号大于 `eventStore.currentVersion(aggregateId)`（无效超前快照），则回退查找 `loadLatestAtOrBefore(aggregateId, currentVersion)` 或从版本 0 起始重放。
- **指定历史版本重建 `loadAtVersion(String aggregateId, long targetVersion)`**：
  - `targetVersion < 0` 或 `targetVersion > eventStore.currentVersion(aggregateId)` 抛出 `IllegalArgumentException`。
  - `targetVersion == 0` 直接返回初始空状态 `InventoryState.empty(aggregateId)`。
  - 优先使用 `snapshotStore.loadLatestAtOrBefore(aggregateId, targetVersion)`（严禁使用版本号 `> targetVersion` 的快照），再通过 `eventStore.readEventsRange(aggregateId, baseVersion, targetVersion)` 增量重放至 `targetVersion`。
- **命令方法**：完整实现并校验乐观锁 `expectedVersion`：
  - `receiveStock(String aggregateId, String batchId, int quantity, long expectedVersion)`
  - `reserveStock(String aggregateId, String orderId, int quantity, long expectedVersion)`
  - `releaseReservation(String aggregateId, String orderId, int quantity, long expectedVersion)`
  - `shipStock(String aggregateId, String orderId, int quantity, long expectedVersion)`
  - 若聚合当前最新版本号与 `expectedVersion` 不一致，抛出 `OptimisticConcurrencyException`。

## 约束条件

- 只允许修改 `src/**/*.java` 范围内的文件。
- 不得修改或删除可见测试文件 `src/com/litmus/es/InventoryPublicTest.java`。
- 仅使用 JDK 17 标准库；全部文件 UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
