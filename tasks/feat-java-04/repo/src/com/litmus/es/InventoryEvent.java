package com.litmus.es;

/**
 * 不可变库存领域事件。
 */
public final class InventoryEvent {
    private final String aggregateId;
    private final long sequence;
    private final EventType type;
    private final String referenceId;
    private final int quantity;
    private final long timestampMillis;

    public InventoryEvent(
            String aggregateId,
            long sequence,
            EventType type,
            String referenceId,
            int quantity,
            long timestampMillis) {
        if (aggregateId == null || aggregateId.isBlank()) {
            throw new IllegalArgumentException("aggregateId 不能为空");
        }
        if (sequence <= 0) {
            throw new IllegalArgumentException("事件序列号必须 >= 1: " + sequence);
        }
        if (type == null) {
            throw new IllegalArgumentException("事件类型不能为空");
        }
        if (referenceId == null || referenceId.isBlank()) {
            throw new IllegalArgumentException("referenceId 不能为空");
        }
        if (quantity <= 0) {
            throw new IllegalArgumentException("数量必须大于 0: " + quantity);
        }
        this.aggregateId = aggregateId;
        this.sequence = sequence;
        this.type = type;
        this.referenceId = referenceId;
        this.quantity = quantity;
        this.timestampMillis = timestampMillis;
    }

    public String getAggregateId() {
        return aggregateId;
    }

    public long getSequence() {
        return sequence;
    }

    public EventType getType() {
        return type;
    }

    public String getReferenceId() {
        return referenceId;
    }

    public int getQuantity() {
        return quantity;
    }

    public long getTimestampMillis() {
        return timestampMillis;
    }
}
