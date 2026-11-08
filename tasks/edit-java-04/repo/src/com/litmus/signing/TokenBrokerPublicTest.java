package com.litmus.signing;

import java.util.concurrent.atomic.AtomicInteger;

/**
 * 可见基础功能测试（单线程缓存、过期、吊销与 LRU）。
 */
public class TokenBrokerPublicTest {
    private static void assertEquals(long expected, long actual, String msg) {
        if (expected != actual) {
            throw new AssertionError(msg + "，期望=" + expected + "，实际=" + actual);
        }
    }

    public void testBasicCacheLifecycle() {
        AtomicInteger seq = new AtomicInteger();
        UpstreamSigner signer = (clientId, issuedAt) -> {
            int n = seq.incrementAndGet();
            return new SignedToken(clientId, clientId + "-tok-" + n, issuedAt, issuedAt + 1000L);
        };
        TokenBroker broker = new TokenBroker(signer, 2, 1000L);

        SignedToken t1 = broker.issueToken("c1", 100L);
        SignedToken t2 = broker.issueToken("c1", 500L);
        if (!t1.tokenValue().equals(t2.tokenValue())) {
            throw new AssertionError("未过期缓存应命中同一令牌");
        }

        SignedToken t3 = broker.issueToken("c2", 600L);
        SignedToken t4 = broker.issueToken("c3", 700L); // 淘汰最久未用的 c1
        if (t3.tokenValue().equals(t4.tokenValue())) {
            throw new AssertionError("不同客户端不应返回相同令牌");
        }

        broker.invalidateClient("c2");
        SignedToken t5 = broker.issueToken("c2", 800L);
        if (t3.tokenValue().equals(t5.tokenValue())) {
            throw new AssertionError("吊销后应重新签发新令牌");
        }

        MetricsSnapshot snap = broker.snapshotMetrics();
        assertEquals(5L, snap.totalRequests(), "总请求数错误");
        assertEquals(1L, snap.cacheHits(), "缓存命中数错误");
        assertEquals(4L, snap.upstreamSignCalls(), "上游签发数错误");
        assertEquals(1L, snap.evictions(), "LRU 淘汰数错误");
        assertEquals(1L, snap.revocations(), "吊销次数错误");
    }
}
