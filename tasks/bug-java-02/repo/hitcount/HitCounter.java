package hitcount;

import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 按键累加命中次数。映射本身可以并发读写，但一次加法不是原子的。
 */
public final class HitCounter {

    private final ConcurrentHashMap<String, Long> counts = new ConcurrentHashMap<String, Long>();

    public void increment(String key, long delta) {
        if (key == null) {
            throw new NullPointerException("key");
        }
        Long current = counts.get(key);
        if (current == null) {
            current = 0L;
        }
        counts.put(key, current + delta);
    }

    public long get(String key) {
        if (key == null) {
            throw new NullPointerException("key");
        }
        Long value = counts.get(key);
        return value == null ? 0L : value.longValue();
    }

    public Map<String, Long> snapshot() {
        return new TreeMap<String, Long>(counts);
    }
}
