package com.litmus.signing;

import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 带缓存、LRU 淘汰与主动吊销能力的令牌签发代理。
 * 当前实现直接在整个方法上加 synchronized，导致慢签名期间全局阻塞。
 */
public final class TokenBroker {
    private final UpstreamSigner signer;
    private final int maxEntries;
    private final long defaultTtlMillis;
    private final Map<String, SignedToken> cache;
    private final Map<String, Long> clientGenerations;

    private long totalRequests;
    private long cacheHits;
    private long upstreamSignCalls;
    private long evictions;
    private long revocations;

    public TokenBroker(UpstreamSigner signer, int maxEntries, long defaultTtlMillis) {
        if (signer == null) {
            throw new IllegalArgumentException("signer 不能为空");
        }
        if (maxEntries <= 0) {
            throw new IllegalArgumentException("maxEntries 必须大于 0");
        }
        if (defaultTtlMillis <= 0) {
            throw new IllegalArgumentException("defaultTtlMillis 必须大于 0");
        }
        this.signer = signer;
        this.maxEntries = maxEntries;
        this.defaultTtlMillis = defaultTtlMillis;
        this.clientGenerations = new LinkedHashMap<>();
        this.cache = new LinkedHashMap<String, SignedToken>(16, 0.75f, true) {
            @Override
            protected boolean removeEldestEntry(Map.Entry<String, SignedToken> eldest) {
                if (size() > TokenBroker.this.maxEntries) {
                    evictions++;
                    return true;
                }
                return false;
            }
        };
    }

    public synchronized SignedToken issueToken(String clientId, long nowEpochMs) {
        if (clientId == null || clientId.trim().isEmpty()) {
            throw new IllegalArgumentException("clientId 不能为空");
        }
        if (nowEpochMs < 0) {
            throw new IllegalArgumentException("nowEpochMs 不能为负");
        }
        String key = clientId.trim();
        totalRequests++;

        SignedToken existing = cache.get(key);
        if (existing != null && existing.expiresAtEpochMs() > nowEpochMs) {
            cacheHits++;
            return existing;
        }
        if (existing != null) {
            cache.remove(key);
        }

        long genBefore = clientGenerations.getOrDefault(key, 0L);
        SignedToken signed = signer.sign(key, nowEpochMs);
        if (signed == null) {
            throw new IllegalStateException("上游返回空令牌");
        }
        upstreamSignCalls++;
        long genAfter = clientGenerations.getOrDefault(key, 0L);
        if (genAfter == genBefore && signed.expiresAtEpochMs() > nowEpochMs) {
            cache.put(key, signed);
        }
        return signed;
    }

    public synchronized void invalidateClient(String clientId) {
        if (clientId == null || clientId.trim().isEmpty()) {
            throw new IllegalArgumentException("clientId 不能为空");
        }
        String key = clientId.trim();
        revocations++;
        long nextGen = clientGenerations.getOrDefault(key, 0L) + 1L;
        clientGenerations.put(key, nextGen);
        cache.remove(key);
    }

    public synchronized int purgeExpired(long nowEpochMs) {
        if (nowEpochMs < 0) {
            throw new IllegalArgumentException("nowEpochMs 不能为负");
        }
        int removed = 0;
        Iterator<Map.Entry<String, SignedToken>> it = cache.entrySet().iterator();
        while (it.hasNext()) {
            if (it.next().getValue().expiresAtEpochMs() <= nowEpochMs) {
                it.remove();
                removed++;
            }
        }
        return removed;
    }

    public synchronized MetricsSnapshot snapshotMetrics() {
        return new MetricsSnapshot(
                totalRequests,
                cacheHits,
                upstreamSignCalls,
                evictions,
                revocations,
                cache.size());
    }

    public long defaultTtlMillis() {
        return defaultTtlMillis;
    }
}
