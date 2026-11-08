package com.litmus.es;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 内存事件日志存储（起始实现未做乐观锁与序列号连续校验）。
 */
public class InMemoryEventStore implements EventStore {
    private final Map<String, List<InventoryEvent>> streams = new HashMap<>();

    @Override
    public synchronized void append(String aggregateId, long expectedVersion, List<InventoryEvent> newEvents) {
        if (aggregateId == null || aggregateId.isBlank() || newEvents == null || newEvents.isEmpty()) {
            throw new IllegalArgumentException("参数不能为空");
        }
        List<InventoryEvent> list = streams.computeIfAbsent(aggregateId, k -> new ArrayList<>());
        list.addAll(newEvents);
    }

    @Override
    public synchronized List<InventoryEvent> readEventsAfter(String aggregateId, long fromVersionExclusive) {
        List<InventoryEvent> list = streams.get(aggregateId);
        if (list == null || list.isEmpty()) {
            return Collections.emptyList();
        }
        List<InventoryEvent> out = new ArrayList<>();
        for (InventoryEvent e : list) {
            if (e.getSequence() > fromVersionExclusive) {
                out.add(e);
            }
        }
        return Collections.unmodifiableList(out);
    }

    @Override
    public synchronized List<InventoryEvent> readEventsRange(
            String aggregateId, long fromVersionExclusive, long toVersionInclusive) {
        List<InventoryEvent> list = streams.get(aggregateId);
        if (list == null || list.isEmpty()) {
            return Collections.emptyList();
        }
        List<InventoryEvent> out = new ArrayList<>();
        for (InventoryEvent e : list) {
            if (e.getSequence() > fromVersionExclusive && e.getSequence() <= toVersionInclusive) {
                out.add(e);
            }
        }
        return Collections.unmodifiableList(out);
    }

    @Override
    public synchronized long currentVersion(String aggregateId) {
        List<InventoryEvent> list = streams.get(aggregateId);
        if (list == null || list.isEmpty()) {
            return 0L;
        }
        return list.get(list.size() - 1).getSequence();
    }
}
