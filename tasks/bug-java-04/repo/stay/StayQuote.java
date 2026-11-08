package stay;

import java.time.Instant;
import java.time.ZoneId;

/**
 * 按入住地日历计算晚数和房费。
 */
public final class StayQuote {

    private StayQuote() {
    }

    public static long nights(Instant checkIn, Instant checkOut, ZoneId zone) {
        return LocalSpan.calendarDaysBetween(checkIn, checkOut, zone);
    }

    public static long totalFen(Instant checkIn, Instant checkOut, ZoneId zone, long nightlyFen) {
        if (nightlyFen < 0) {
            throw new IllegalArgumentException("房价不能为负");
        }
        long nights = nights(checkIn, checkOut, zone);
        if (nights < 0) {
            throw new IllegalArgumentException("退房早于入住");
        }
        return Math.multiplyExact(nights, nightlyFen);
    }
}
