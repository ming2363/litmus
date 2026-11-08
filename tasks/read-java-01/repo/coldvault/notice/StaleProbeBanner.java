package coldvault.notice;

/** 告示文字。不读取配置表。 */
public final class StaleProbeBanner {
    public String text() {
        return "告示：阈值键 vault.probe.stale.minutes 的含义见运维手册";
    }
}
