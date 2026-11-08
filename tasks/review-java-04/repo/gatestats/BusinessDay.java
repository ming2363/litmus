package gatestats;

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;

/** 业务日按 Asia/Shanghai 切分，不跟随运行机器的默认时区。 */
public final class BusinessDay {
    private BusinessDay() {
    }

    public static LocalDate businessDate(long epochMillis) {
        return Instant.ofEpochMilli(epochMillis).atZone(ZoneId.systemDefault()).toLocalDate();
    }

    public static String formatShanghai(long epochMillis) {
        return Instant.ofEpochMilli(epochMillis).atZone(ZoneId.of("Asia/Shanghai")).toString();
    }
}
