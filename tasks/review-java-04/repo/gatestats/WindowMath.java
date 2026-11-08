package gatestats;

/** 统计窗口。最长 90 天。 */
public final class WindowMath {
    public static final int MAX_WINDOW_MINUTES = 90 * 24 * 60;

    private WindowMath() {
    }

    /** 把允许范围内的分钟换成毫秒。 */
    public static int windowMillis(int minutes) {
        if (minutes < 0 || minutes > MAX_WINDOW_MINUTES) {
            throw new IllegalArgumentException("minutes");
        }
        return minutes * 60 * 1000;
    }
}
