package coldvault.report;

import coldvault.config.ConfigStore;

/** 日报里统计过期探针。 */
public final class StaleProbeDigest {
    private final ConfigStore store;

    public StaleProbeDigest(ConfigStore store) {
        this.store = store;
    }

    public long limitMinutes() {
        return store.getLong("vault.probe.stale.minutes", 15L);
    }
}
