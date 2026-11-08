package admission;

public class VisitPublicTest {

    public void testEqualCountsEvictOldest() {
        VisitCache cache = new VisitCache(2);
        cache.put("A", "a");
        cache.put("B", "b");
        cache.put("C", "c");
        eq(cache.size(), 2, "容量");
        if (cache.get("A") != null) {
            throw new AssertionError("次数相同时应淘汰最早的 A");
        }
        eqStr(cache.get("B"), "b", "B 还在");
        eqStr(cache.get("C"), "c", "C 还在");
    }

    public void testUpdateDoesNotEvict() {
        VisitCache cache = new VisitCache(1);
        cache.put("A", "a");
        cache.put("A", "a2");
        eq(cache.size(), 1, "更新不扩容");
        eqStr(cache.get("A"), "a2", "新值");
        eq(cache.accessCount("A"), 3, "两次 put 和一次 get");
    }

    public void testMissDoesNotInsert() {
        VisitCache cache = new VisitCache(2);
        if (cache.get("missing") != null) {
            throw new AssertionError("未命中应返回 null");
        }
        eq(cache.size(), 0, "未命中不占容量");
        eq(cache.accessCount("missing"), 0, "未命中没有次数");
    }

    public void testRejectsBadArguments() {
        try {
            new VisitCache(0);
            throw new AssertionError("容量 0 应被拒绝");
        } catch (IllegalArgumentException expected) {
            // 预期异常
        }
        VisitCache cache = new VisitCache(1);
        try {
            cache.put(null, "a");
            throw new AssertionError("空键应被拒绝");
        } catch (NullPointerException expected) {
            // 预期异常
        }
        try {
            cache.get(null);
            throw new AssertionError("读取空键应被拒绝");
        } catch (NullPointerException expected) {
            // 预期异常
        }
    }

    public void testCountsBeforeEviction() {
        VisitCache cache = new VisitCache(3);
        cache.put("A", "a");
        cache.get("A");
        cache.put("B", "b");
        eq(cache.accessCount("A"), 2, "A 的次数");
        eq(cache.accessCount("B"), 1, "B 的次数");
        eq(cache.size(), 2, "尚未淘汰");
    }

    private static void eq(int actual, int expected, String label) {
        if (actual != expected) {
            throw new AssertionError(label + "，期望 " + expected + " 实际 " + actual);
        }
    }

    private static void eqStr(String actual, String expected, String label) {
        if (actual == null || !actual.equals(expected)) {
            throw new AssertionError(label + "，期望 " + expected + " 实际 " + actual);
        }
    }
}
