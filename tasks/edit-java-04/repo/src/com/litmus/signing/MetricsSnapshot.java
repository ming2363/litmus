package com.litmus.signing;

/**
 * 不可变代理运行指标快照。
 */
public final class MetricsSnapshot {
    private final long totalRequests;
    private final long cacheHits;
    private final long upstreamSignCalls;
    private final long evictions;
    private final long revocations;
    private final int cacheSize;

    public MetricsSnapshot(
            long totalRequests,
            long cacheHits,
            long upstreamSignCalls,
            long evictions,
            long revocations,
            int cacheSize) {
        this.totalRequests = totalRequests;
        this.cacheHits = cacheHits;
        this.upstreamSignCalls = upstreamSignCalls;
        this.evictions = evictions;
        this.revocations = revocations;
        this.cacheSize = cacheSize;
    }

    public long totalRequests() {
        return totalRequests;
    }

    public long cacheHits() {
        return cacheHits;
    }

    public long upstreamSignCalls() {
        return upstreamSignCalls;
    }

    public long evictions() {
        return evictions;
    }

    public long revocations() {
        return revocations;
    }

    public int cacheSize() {
        return cacheSize;
    }
}
