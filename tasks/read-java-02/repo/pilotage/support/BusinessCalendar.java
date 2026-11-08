package pilotage.support;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/** 2026 年业务日历。节假日写死在代码里。 */
public final class BusinessCalendar {
    private static final DateTimeFormatter ISO = DateTimeFormatter.ISO_LOCAL_DATE;
    private static final Set<LocalDate> HOLIDAYS = buildHolidays();
    private static final Set<LocalDate> EXTRA = buildExtra();

    private BusinessCalendar() {
    }

    public static LocalDate parseDate(String text) {
        if (text == null || text.length() != 10) {
            throw new IllegalArgumentException(String.valueOf(text));
        }
        try {
            return LocalDate.parse(text, ISO);
        } catch (DateTimeParseException exc) {
            throw new IllegalArgumentException(text);
        }
    }

    public static boolean isBusinessDay(LocalDate day) {
        if (HOLIDAYS.contains(day)) {
            return false;
        }
        if (EXTRA.contains(day)) {
            return true;
        }
        int weekday = day.getDayOfWeek().getValue();
        return weekday < 6;
    }

    public static LocalDate addBusinessDays(LocalDate day, int count) {
        if (count == 0) {
            return day;
        }
        int step = count > 0 ? 1 : -1;
        int left = Math.abs(count);
        LocalDate cursor = day;
        while (left > 0) {
            cursor = cursor.plusDays(step);
            if (isBusinessDay(cursor)) {
                left -= 1;
            }
        }
        return cursor;
    }

    public static int businessSpan(LocalDate start, LocalDate end) {
        if (end.isBefore(start)) {
            return 0;
        }
        int total = 0;
        LocalDate cursor = start;
        while (!cursor.isAfter(end)) {
            if (isBusinessDay(cursor)) {
                total += 1;
            }
            cursor = cursor.plusDays(1);
        }
        return total;
    }

    private static Set<LocalDate> buildHolidays() {
        Set<LocalDate> days = new HashSet<LocalDate>();
        days.add(LocalDate.of(2026, 1, 1));
        days.add(LocalDate.of(2026, 2, 16));
        days.add(LocalDate.of(2026, 2, 17));
        days.add(LocalDate.of(2026, 2, 18));
        days.add(LocalDate.of(2026, 2, 19));
        days.add(LocalDate.of(2026, 4, 6));
        days.add(LocalDate.of(2026, 5, 1));
        days.add(LocalDate.of(2026, 6, 19));
        days.add(LocalDate.of(2026, 10, 1));
        days.add(LocalDate.of(2026, 10, 2));
        days.add(LocalDate.of(2026, 10, 5));
        return Collections.unmodifiableSet(days);
    }

    private static Set<LocalDate> buildExtra() {
        Set<LocalDate> days = new HashSet<LocalDate>();
        days.add(LocalDate.of(2026, 2, 14));
        days.add(LocalDate.of(2026, 10, 10));
        return Collections.unmodifiableSet(days);
    }
}
