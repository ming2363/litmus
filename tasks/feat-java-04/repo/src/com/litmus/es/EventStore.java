package com.litmus.es;

import java.util.List;

/**
 * 聚合事件日志存储接口。
 */
public interface EventStore {
    void append(String aggregateId, long expectedVersion, List<InventoryEvent> newEvents);

    List<InventoryEvent> readEventsAfter(String aggregateId, long fromVersionExclusive);

    List<InventoryEvent> readEventsRange(String aggregateId, long fromVersionExclusive, long toVersionInclusive);

    long currentVersion(String aggregateId);
}
