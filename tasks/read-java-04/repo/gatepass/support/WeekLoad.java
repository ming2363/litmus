package gatepass.support;

import java.time.LocalDate;

/** 按星期汇总。星期一是 0。 */
public final class WeekLoad {
    private WeekLoad() {
    }

    public static int[] byWeekday(LocalDate[] days, int[] amounts) {
        if (days.length != amounts.length) {
            throw new IllegalArgumentException("width");
        }
        int[] loads = new int[7];
        for (int i = 0; i < days.length; i++) {
            int idx = days[i].getDayOfWeek().getValue() - 1;
            loads[idx] += amounts[i];
        }
        return loads;
    }

    public static int peak(LocalDate[] days, int[] amounts) {
        int[] loads = byWeekday(days, amounts);
        int best = 0;
        for (int i = 1; i < loads.length; i++) {
            if (loads[i] > loads[best]) {
                best = i;
            }
        }
        return best;
    }
}
