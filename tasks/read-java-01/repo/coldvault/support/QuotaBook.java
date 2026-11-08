package coldvault.support;

import java.util.HashMap;
import java.util.Map;

/** 单线程配额账本。 */
public final class QuotaBook {
    private final Map<String, Integer> limits;
    private final Map<String, Integer> used = new HashMap<String, Integer>();

    public QuotaBook(Map<String, Integer> limits) {
        this.limits = new HashMap<String, Integer>(limits);
        for (String key : this.limits.keySet()) {
            used.put(key, Integer.valueOf(0));
        }
    }

    public int remaining(String key) {
        if (!limits.containsKey(key)) {
            throw new IllegalArgumentException(key);
        }
        return limits.get(key).intValue() - used.get(key).intValue();
    }

    public boolean tryTake(String key, int amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("amount");
        }
        if (remaining(key) < amount) {
            return false;
        }
        used.put(key, Integer.valueOf(used.get(key).intValue() + amount));
        return true;
    }

    public void refund(String key, int amount) {
        int have = used.containsKey(key) ? used.get(key).intValue() : 0;
        if (amount <= 0 || amount > have) {
            throw new IllegalArgumentException("refund");
        }
        used.put(key, Integer.valueOf(have - amount));
    }
}
