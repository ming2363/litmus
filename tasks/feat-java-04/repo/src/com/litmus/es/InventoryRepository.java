package com.litmus.es;

import java.util.List;

/**
 * 库存聚合仓储服务（起始版本仅支持从 0 全量重放与入库/预占命令）。
 */
public class InventoryRepository {
    private final EventStore eventStore;
    private final SnapshotStore snapshotStore;
    private final int snapshotInterval;

    public InventoryRepository(EventStore eventStore, SnapshotStore snapshotStore, int snapshotInterval) {
        if (eventStore == null || snapshotStore == null) {
            throw new IllegalArgumentException("EventStore 与 SnapshotStore 不能为空");
        }
        if (snapshotInterval < 0) {
            throw new IllegalArgumentException("snapshotInterval 不能为负");
        }
        this.eventStore = eventStore;
        this.snapshotStore = snapshotStore;
        this.snapshotInterval = snapshotInterval;
    }

    public InventoryState load(String aggregateId) {
        InventoryState state = InventoryState.empty(aggregateId);
        List<InventoryEvent> events = eventStore.readEventsAfter(aggregateId, 0L);
        for (InventoryEvent e : events) {
            state = state.apply(e);
        }
        return state;
    }

    public InventoryState loadAtVersion(String aggregateId, long targetVersion) {
        throw new UnsupportedOperationException("loadAtVersion 尚未实现");
    }

    public InventoryState receiveStock(String aggregateId, String batchId, int quantity, long expectedVersion) {
        InventoryState current = load(aggregateId);
        InventoryEvent evt = new InventoryEvent(
                aggregateId,
                expectedVersion + 1,
                EventType.STOCK_RECEIVED,
                batchId,
                quantity,
                System.currentTimeMillis()
        );
        InventoryState next = current.apply(evt);
        eventStore.append(aggregateId, expectedVersion, List.of(evt));
        return next;
    }

    public InventoryState reserveStock(String aggregateId, String orderId, int quantity, long expectedVersion) {
        InventoryState current = load(aggregateId);
        InventoryEvent evt = new InventoryEvent(
                aggregateId,
                expectedVersion + 1,
                EventType.STOCK_RESERVED,
                orderId,
                quantity,
                System.currentTimeMillis()
        );
        InventoryState next = current.apply(evt);
        eventStore.append(aggregateId, expectedVersion, List.of(evt));
        return next;
    }

    public InventoryState releaseReservation(String aggregateId, String orderId, int quantity, long expectedVersion) {
        throw new UnsupportedOperationException("releaseReservation 尚未实现");
    }

    public InventoryState shipStock(String aggregateId, String orderId, int quantity, long expectedVersion) {
        throw new UnsupportedOperationException("shipStock 尚未实现");
    }
}
