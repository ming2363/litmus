package coldvault.ops;

import coldvault.config.ConfigStore;

/** 采样是否还新鲜。 */
public final class ProbeFreshnessGate {
    private final ConfigStore store;

    public ProbeFreshnessGate(ConfigStore store) {
        this.store = store;
    }

    /** 超过分钟数则拒绝使用该采样。 */
    public boolean fresh(int ageMinutes) {
        int limit = store.getInt("vault.probe.stale.minutes", 15);
        return ageMinutes >= 0 && ageMinutes <= limit;
    }
}
