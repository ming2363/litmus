package coldvault.ops;

/** 温区分档，与过期分钟无关。 */
public final class ZoneBand {
    public String band(int celsius) {
        if (celsius <= -18) {
            return "frozen";
        }
        if (celsius <= 4) {
            return "chilled";
        }
        return "warm";
    }
}
