package com.litmus.es;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 不可变库存聚合状态（起始版本仅实现了入库与预占事件）。
 */
public final class InventoryState {
    private final String aggregateId;
    private final long version;
    private final int onHand;
    private final int reserved;
    private final Map<String, Integer> reservations;

    public InventoryState(
            String aggregateId,
            long version,
            int onHand,
            int reserved,
            Map<String, Integer> reservations) {
        if (aggregateId == null || aggregateId.isBlank()) {
            throw new IllegalArgumentException("aggregateId 不能为空");
        }
        this.aggregateId = aggregateId;
        this.version = version;
        this.onHand = onHand;
        this.reserved = reserved;
        this.reservations = reservations == null
                ? Collections.emptyMap()
                : Collections.unmodifiableMap(new LinkedHashMap<>(reservations));
    }

    public static InventoryState empty(String aggregateId) {
        return new InventoryState(aggregateId, 0L, 0, 0, Collections.emptyMap());
    }

    public String getAggregateId() {
        return aggregateId;
    }

    public long getVersion() {
        return version;
    }

    public int getOnHand() {
        return onHand;
    }

    public int getReserved() {
        return reserved;
    }

    public int available() {
        return onHand - reserved;
    }

    public Map<String, Integer> getReservations() {
        return reservations;
    }

    public InventoryState apply(InventoryEvent event) {
        if (event == null || !aggregateId.equals(event.getAggregateId())) {
            throw new IllegalArgumentException("事件与聚合 ID 不匹配");
        }
        if (event.getSequence() != version + 1) {
            throw new IllegalStateException(
                    "事件序号不连续: expected=" + (version + 1) + ", actual=" + event.getSequence());
        }
        Map<String, Integer> nextMap = new LinkedHashMap<>(reservations);
        switch (event.getType()) {
            case STOCK_RECEIVED:
                return new InventoryState(
                        aggregateId,
                        event.getSequence(),
                        onHand + event.getQuantity(),
                        reserved,
                        nextMap
                );
            case STOCK_RESERVED:
                if (available() < event.getQuantity()) {
                    throw new IllegalStateException("可用库存不足，无法预占");
                }
                nextMap.merge(event.getReferenceId(), event.getQuantity(), Integer::sum);
                return new InventoryState(
                        aggregateId,
                        event.getSequence(),
                        onHand,
                        reserved + event.getQuantity(),
                        nextMap
                );
            case RESERVATION_RELEASED:
            case STOCK_SHIPPED:
                throw new UnsupportedOperationException("事件类型尚未实现: " + event.getType());
            default:
                throw new IllegalArgumentException("未知事件类型: " + event.getType());
        }
    }
}
