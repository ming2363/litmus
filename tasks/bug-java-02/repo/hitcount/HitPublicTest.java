package hitcount;

import java.util.Map;

public class HitPublicTest {

    public void testSingleThreadSum() {
        HitCounter counter = new HitCounter();
        eq(counter.get("missing"), 0L, "缺键为 0");
        counter.increment("door", 2L);
        counter.increment("door", 3L);
        counter.increment("door", -1L);
        counter.increment("Window", 4L);
        eq(counter.get("door"), 4L, "同键累加");
        eq(counter.get("Window"), 4L, "大小写不同");
        eq(counter.get("window"), 0L, "不合并大小写");
    }

    public void testSnapshotIsIsolatedAndSorted() {
        HitCounter counter = new HitCounter();
        counter.increment("b", 1L);
        counter.increment("a", 2L);
        Map<String, Long> shot = counter.snapshot();
        shot.put("a", 9L);
        shot.put("c", 3L);
        counter.increment("a", 1L);
        eq(counter.get("a"), 3L, "快照被改写后计数器不变");
        String rendered = HitReport.render(counter);
        if (!"a=3\nb=1\n".equals(rendered)) {
            throw new AssertionError("渲染结果不对: " + rendered);
        }
    }

    public void testNullKey() {
        HitCounter counter = new HitCounter();
        try {
            counter.increment(null, 1L);
            throw new AssertionError("空键应抛出空指针");
        } catch (NullPointerException expected) {
            // 预期异常
        }
        try {
            counter.get(null);
            throw new AssertionError("读取空键应抛出空指针");
        } catch (NullPointerException expected) {
            // 预期异常
        }
    }

    public void testZeroDeltaKeepsExisting() {
        HitCounter counter = new HitCounter();
        counter.increment("k", 0L);
        eq(counter.get("k"), 0L, "从零加上 0");
        counter.increment("k", 5L);
        counter.increment("k", 0L);
        eq(counter.get("k"), 5L, "加上 0 不改变原值");
    }

    private static void eq(long actual, long expected, String label) {
        if (actual != expected) {
            throw new AssertionError(label + "，期望 " + expected + " 实际 " + actual);
        }
    }
}
