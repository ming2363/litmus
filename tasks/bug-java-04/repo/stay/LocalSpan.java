package stay;

import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;

/**
 * 用物理时长折算两个时刻相差的整天数。
 */
public final class LocalSpan {

    private LocalSpan() {
    }

    public static long calendarDaysBetween(Instant start, Instant end, ZoneId zone) {
        if (start == null || end == null || zone == null) {
            throw new NullPointerException("start/end/zone");
        }
        return Duration.between(start, end).toDays();
    }
}
