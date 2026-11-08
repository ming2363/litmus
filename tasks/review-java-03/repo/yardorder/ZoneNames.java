package yardorder;

/** 箱区名称归一。 */
public final class ZoneNames {
    private ZoneNames() {
    }

    public static String normalize(String zone) {
        if (zone == null) {
            return "";
        }
        return zone.trim().toUpperCase();
    }
}
