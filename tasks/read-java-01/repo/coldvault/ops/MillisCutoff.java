package coldvault.ops;

import coldvault.config.ConfigStore;

/** 另一套毫秒阈值，不是分钟键。 */
public final class MillisCutoff {
    private final ConfigStore store;

    public MillisCutoff(ConfigStore store) {
        this.store = store;
    }

    public boolean freshMillis(long ageMillis) {
        int limit = store.getInt("vault.probe.stale.millis", 900000);
        return ageMillis >= 0 && ageMillis <= limit;
    }
}
