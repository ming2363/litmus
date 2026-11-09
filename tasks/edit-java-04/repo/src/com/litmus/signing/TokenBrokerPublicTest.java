package com.litmus.signing;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/** 可见测试。签名重叠是目前唯一会失败的行为。 */
public class TokenBrokerPublicTest {

    public void testIssueStoresMaterial() {
        ManualClock clock = new ManualClock();
        clock.now = 1000L;
        EchoSigner signer = new EchoSigner();
        TokenBroker broker = new TokenBroker(signer, clock, 4);
        TokenBroker.Token token = broker.issueToken("acme", "reefer", 500L);
        String text = "acme\nreefer\n1500";
        check(token.expiresAt == 1500L, "到期时刻");
        check(Arrays.equals(token.signature, text.getBytes(StandardCharsets.UTF_8)), "待签字节");
        check(signer.calls == 1, "应签名一次");
        TokenBroker.Snapshot snap = broker.snapshot();
        check(snap.totalRequests == 1L, "total");
        check(snap.cacheHits == 0L, "hits");
        check(snap.upstreamSignCalls == 1L, "sign");
        check(snap.evictionCount == 0L, "evict");
        check(snap.cacheSize == 1, "size");
        check(snap.epoch == 0, "epoch");
    }

    public void testCacheHitSkipsSigner() {
        ManualClock clock = new ManualClock();
        clock.now = 10L;
        EchoSigner signer = new EchoSigner();
        TokenBroker broker = new TokenBroker(signer, clock, 4);
        TokenBroker.Token first = broker.issueToken("acme", "box", 40L);
        TokenBroker.Token second = broker.issueToken("acme", "box", 40L);
        check(first == second, "命中应返回缓存对象");
        check(signer.calls == 1, "命中不能再签名");
        TokenBroker.Snapshot snap = broker.snapshot();
        check(snap.totalRequests == 2L && snap.cacheHits == 1L && snap.upstreamSignCalls == 1L, "计数");
    }

    public void testExpiredLookupIsNotEviction() {
        ManualClock clock = new ManualClock();
        clock.now = 100L;
        EchoSigner signer = new EchoSigner();
        TokenBroker broker = new TokenBroker(signer, clock, 4);
        broker.issueToken("acme", "box", 50L);
        clock.now = 150L;
        check(broker.lookup("acme", "box") == null, "到期时刻等于 now 视为过期");
        TokenBroker.Snapshot snap = broker.snapshot();
        check(snap.evictionCount == 0L, "过期移除不计淘汰");
        check(snap.cacheSize == 0, "过期后缓存为空");
        broker.issueToken("acme", "box", 50L);
        check(signer.calls == 2, "过期后要重新签名");
        check(broker.snapshot().evictionCount == 0L, "重新签发仍不是容量淘汰");
    }

    public void testLruEvictsLeastRecent() {
        ManualClock clock = new ManualClock();
        clock.now = 1L;
        EchoSigner signer = new EchoSigner();
        TokenBroker broker = new TokenBroker(signer, clock, 2);
        broker.issueToken("c", "a", 100L);
        broker.issueToken("c", "b", 100L);
        broker.issueToken("c", "a", 100L);
        broker.issueToken("c", "c", 100L);
        check(broker.lookup("c", "b") == null, "最久未使用的 b 被淘汰");
        check(broker.lookup("c", "a") != null, "a 仍在");
        check(broker.lookup("c", "c") != null, "c 仍在");
        check(broker.snapshot().evictionCount == 1L, "容量淘汰加一");
    }

    public void testRejectsBlankAndNonPositiveTtl() {
        ManualClock clock = new ManualClock();
        clock.now = 1L;
        EchoSigner signer = new EchoSigner();
        TokenBroker broker = new TokenBroker(signer, clock, 2);
        broker.issueToken("acme", "box", 5L);
        expectIae(new Runnable() {
            public void run() { broker.issueToken(null, "box", 5L); }
        });
        expectIae(new Runnable() {
            public void run() { broker.issueToken("  ", "box", 5L); }
        });
        expectIae(new Runnable() {
            public void run() { broker.issueToken("acme", "", 5L); }
        });
        expectIae(new Runnable() {
            public void run() { broker.issueToken("acme", "box", 0L); }
        });
        expectIae(new Runnable() {
            public void run() { broker.issueToken("acme", "box", -3L); }
        });
        check(signer.calls == 1, "非法参数不能签名");
        check(broker.snapshot().totalRequests == 1L, "非法参数不能加计数");
        check(broker.lookup("acme", "box") != null, "原缓存还在");
    }

    public void testInvalidateClearsWithoutResettingMetrics() {
        ManualClock clock = new ManualClock();
        clock.now = 5L;
        EchoSigner signer = new EchoSigner();
        TokenBroker broker = new TokenBroker(signer, clock, 3);
        broker.issueToken("acme", "box", 9L);
        broker.invalidate();
        TokenBroker.Snapshot snap = broker.snapshot();
        check(broker.lookup("acme", "box") == null, "清空");
        check(snap.cacheSize == 0, "size");
        check(snap.epoch == 1, "epoch");
        check(snap.totalRequests == 1L && snap.upstreamSignCalls == 1L && snap.cacheHits == 0L, "计数保留");
    }

    public void testSnapshotMatchesCounters() {
        ManualClock clock = new ManualClock();
        clock.now = 8L;
        EchoSigner signer = new EchoSigner();
        TokenBroker broker = new TokenBroker(signer, clock, 4);
        broker.issueToken("a", "one", 10L);
        broker.issueToken("a", "one", 10L);
        broker.issueToken("a", "two", 10L);
        TokenBroker.Snapshot snap = broker.snapshot();
        check(snap.totalRequests == 3L, "total");
        check(snap.cacheHits == 1L, "hits");
        check(snap.upstreamSignCalls == 2L, "signs");
        check(snap.totalRequests == snap.cacheHits + snap.upstreamSignCalls, "恒等");
        check(snap.cacheSize == 2, "两个键");
    }

    public void testRejectsBadCapacity() {
        ManualClock clock = new ManualClock();
        EchoSigner signer = new EchoSigner();
        expectIae(new Runnable() {
            public void run() { new TokenBroker(signer, clock, 0); }
        });
        expectNpe(new Runnable() {
            public void run() { new TokenBroker(null, clock, 1); }
        });
        expectNpe(new Runnable() {
            public void run() { new TokenBroker(signer, null, 1); }
        });
    }

    public void testConcurrentSignOverlap() throws Exception {
        ManualClock clock = new ManualClock();
        clock.now = 20L;
        GateSigner signer = new GateSigner();
        TokenBroker broker = new TokenBroker(signer, clock, 4);
        Holder left = start(broker, "c1", "a", 30L);
        Holder right = start(broker, "c2", "b", 30L);
        try {
            check(signer.awaitEntered(0, 400), "第一路应进入签名");
            check(signer.awaitEntered(1, 400), "第二路应在第一路返回前进入签名");
        } finally {
            signer.releaseAll();
            left.join();
            right.join();
        }
        check(left.token != null && right.token != null, "两路都要返回令牌");
        check(left.error == null && right.error == null, "签名线程不应抛错");
    }

    private static Holder start(final TokenBroker broker, final String client, final String subject, final long ttl) {
        final Holder holder = new Holder();
        holder.thread = new Thread(new Runnable() {
            public void run() {
                try {
                    holder.token = broker.issueToken(client, subject, ttl);
                } catch (Throwable ex) {
                    holder.error = ex;
                }
            }
        });
        holder.thread.start();
        return holder;
    }

    private static void expectIae(Runnable runnable) {
        try {
            runnable.run();
        } catch (IllegalArgumentException ex) {
            return;
        }
        throw new AssertionError("应抛出 IllegalArgumentException");
    }

    private static void expectNpe(Runnable runnable) {
        try {
            runnable.run();
        } catch (NullPointerException ex) {
            return;
        }
        throw new AssertionError("应抛出 NullPointerException");
    }

    private static void check(boolean cond, String message) {
        if (!cond) {
            throw new AssertionError(message);
        }
    }

    static final class ManualClock implements TokenBroker.Clock {
        long now;
        public long now() { return now; }
    }

    static final class EchoSigner implements TokenBroker.Signer {
        int calls;
        public byte[] sign(byte[] material) {
            calls++;
            return material.clone();
        }
    }

    static final class Holder {
        Thread thread;
        TokenBroker.Token token;
        Throwable error;
        void join() throws InterruptedException {
            thread.join(2000L);
        }
    }

    static final class GateSigner implements TokenBroker.Signer {
        private final java.util.List<CountDownLatch> gates = new java.util.ArrayList<CountDownLatch>();
        private final java.util.List<CountDownLatch> startedFlags = new java.util.ArrayList<CountDownLatch>();
        private volatile boolean open;

        public byte[] sign(byte[] material) {
            CountDownLatch gate = new CountDownLatch(1);
            CountDownLatch started = new CountDownLatch(1);
            synchronized (this) {
                gates.add(gate);
                startedFlags.add(started);
            }
            started.countDown();
            if (!open) {
                try {
                    gate.await(1500L, TimeUnit.MILLISECONDS);
                } catch (InterruptedException ex) {
                    Thread.currentThread().interrupt();
                }
            }
            return material.clone();
        }

        boolean awaitEntered(int index, long millis) throws InterruptedException {
            long deadline = System.nanoTime() + millis * 1000000L;
            while (System.nanoTime() < deadline) {
                CountDownLatch started = null;
                synchronized (this) {
                    if (startedFlags.size() > index) {
                        started = startedFlags.get(index);
                    }
                }
                if (started != null && started.await(20L, TimeUnit.MILLISECONDS)) {
                    return true;
                }
            }
            return false;
        }

        void releaseAll() {
            open = true;
            CountDownLatch[] copy;
            synchronized (this) {
                copy = gates.toArray(new CountDownLatch[0]);
            }
            for (int i = 0; i < copy.length; i++) {
                copy[i].countDown();
            }
        }
    }
}
