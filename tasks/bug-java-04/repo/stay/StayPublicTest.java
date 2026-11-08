package stay;

import java.time.Instant;
import java.time.ZoneId;

public class StayPublicTest {

    public void testExactShanghaiDays() {
        ZoneId zone = ZoneId.of("Asia/Shanghai");
        Instant start = Instant.parse("2025-12-31T16:00:00Z");
        Instant end = Instant.parse("2026-01-02T16:00:00Z");
        eq(LocalSpan.calendarDaysBetween(start, end, zone), 2L, "整整两天");
        eq(StayQuote.totalFen(start, end, zone, 3500L), 7000L, "房费");
    }

    public void testSameInstantAndSameLocalDay() {
        ZoneId zone = ZoneId.of("Asia/Shanghai");
        Instant start = Instant.parse("2026-01-01T01:00:00Z");
        eq(LocalSpan.calendarDaysBetween(start, start, zone), 0L, "同一时刻");
        Instant later = Instant.parse("2026-01-01T10:00:00Z");
        eq(LocalSpan.calendarDaysBetween(start, later, zone), 0L, "同一本地日");
        eq(StayQuote.totalFen(start, later, zone, 100L), 0L, "零晚房费");
    }

    public void testNegativeExactDays() {
        ZoneId zone = ZoneId.of("Asia/Shanghai");
        Instant start = Instant.parse("2026-01-03T16:00:00Z");
        Instant end = Instant.parse("2026-01-01T16:00:00Z");
        eq(LocalSpan.calendarDaysBetween(start, end, zone), -2L, "反向两天");
        try {
            StayQuote.totalFen(start, end, zone, 100L);
            throw new AssertionError("退房更早应被拒绝");
        } catch (IllegalArgumentException ex) {
            if (ex.getMessage() == null || !ex.getMessage().contains("退房")) {
                throw new AssertionError("异常消息应提到退房");
            }
        }
    }

    public void testNullRejected() {
        try {
            LocalSpan.calendarDaysBetween(null, Instant.EPOCH, ZoneId.of("UTC"));
            throw new AssertionError("空起点应被拒绝");
        } catch (NullPointerException expected) {
            // 预期异常
        }
    }

    private static void eq(long actual, long expected, String label) {
        if (actual != expected) {
            throw new AssertionError(label + "，期望 " + expected + " 实际 " + actual);
        }
    }
}
