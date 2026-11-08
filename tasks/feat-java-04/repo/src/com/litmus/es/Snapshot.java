package com.litmus.es;

/**
 * 聚合快照记录。
 */
public final class Snapshot {
    private final String aggregateId;
    private final long version;
    private final InventoryState state;

    public Snapshot(String aggregateId, long version, InventoryState state) {
        if (aggregateId == null || aggregateId.isBlank() || state == null) {
            throw new IllegalArgumentException("快照参数非法");
        }
        if (version < 0 || state.getVersion() != version || !aggregateId.equals(state.getAggregateId())) {
            throw new IllegalArgumentException("快照版本或聚合 ID 不一致");
        }
        this.aggregateId = aggregateId;
        this.version = version;
        this.state = new InventoryState(
                state.getAggregateId(),
                state.getVersion(),
                state.getOnHand(),
                state.getReserved(),
                state.getReservations()
        );
    }

    public String getAggregateId() {
        return aggregateId;
    }

    public long getVersion() {
        return version;
    }

    public InventoryState getState() {
        return state;
    }
}
