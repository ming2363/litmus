package coldvault.config;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

/** 字符串配置表。 */
public final class ConfigStore {
    private final Map<String, String> values;

    public ConfigStore(Map<String, String> values) {
        this.values = Collections.unmodifiableMap(new HashMap<String, String>(values));
    }

    /** 缺少键时返回 null。 */
    public String get(String key) {
        return values.get(key);
    }

    /** 缺键或空白时返回 fallback。 */
    public int getInt(String key, int fallback) {
        String raw = get(key);
        if (raw == null || raw.trim().isEmpty()) {
            return fallback;
        }
        return Integer.parseInt(raw.trim());
    }

    /** 缺键或空白时返回 fallback。 */
    public long getLong(String key, long fallback) {
        String raw = get(key);
        if (raw == null || raw.trim().isEmpty()) {
            return fallback;
        }
        return Long.parseLong(raw.trim());
    }
}
