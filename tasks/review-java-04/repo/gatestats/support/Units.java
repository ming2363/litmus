package gatestats.support;

/** 单位换算。分钟转毫秒走 long，避免静默溢出。 */
public final class Units {
    private Units() {
    }

    public static int cmToMm(int cm) {
        if (cm < 0) {
            throw new IllegalArgumentException("cm");
        }
        return cm * 10;
    }

    public static long minutesToMillis(int minutes, int ceiling) {
        if (minutes < 0 || minutes > ceiling) {
            throw new IllegalArgumentException("minutes");
        }
        return minutes * 60L * 1000L;
    }

    public static int clamp(int value, int low, int high) {
        if (low > high) {
            throw new IllegalArgumentException("range");
        }
        return Math.min(Math.max(value, low), high);
    }
}
