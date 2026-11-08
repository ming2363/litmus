package coldvault.sync;

import coldvault.config.ConfigStore;

/** 夜间清扫任务读取同一分钟键。 */
public final class NightlyProbeSweep {
    private final ConfigStore store;

    public NightlyProbeSweep(ConfigStore store) {
        this.store = store;
    }

    public String configuredLimit() {
        String raw = store.get("vault.probe.stale.minutes");
        if (raw == null || raw.trim().isEmpty()) {
            return "15";
        }
        return raw.trim();
    }
}
