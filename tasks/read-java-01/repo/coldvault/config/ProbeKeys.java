package coldvault.config;

/** 键名常量。本类不读取配置值。 */
public final class ProbeKeys {
    public static final String STALE_MINUTES = "vault.probe.stale.minutes";
    public static final String STALE_MILLIS = "vault.probe.stale.millis";

    private ProbeKeys() {
    }
}
