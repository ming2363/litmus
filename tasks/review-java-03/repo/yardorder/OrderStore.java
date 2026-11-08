package yardorder;

import java.util.HashMap;
import java.util.Map;

/** 订单箱区的内存存储。 */
public final class OrderStore {
    private final Map<String, String> zones = new HashMap<String, String>();

    public void save(String id, String zone) {
        zones.put(id, zone);
    }

    public String load(String id) {
        return zones.get(id);
    }
}
