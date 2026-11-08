package gatepass.support;

import java.util.Arrays;

/** 小样本统计。 */
public final class StatsKit {
    private StatsKit() {
    }

    public static double mean(int[] values) {
        if (values.length == 0) {
            throw new IllegalArgumentException("empty");
        }
        long total = 0L;
        for (int i = 0; i < values.length; i++) {
            total += values[i];
        }
        return total / (double) values.length;
    }

    public static double median(int[] values) {
        if (values.length == 0) {
            throw new IllegalArgumentException("empty");
        }
        int[] copy = Arrays.copyOf(values, values.length);
        Arrays.sort(copy);
        int mid = copy.length / 2;
        if (copy.length % 2 == 1) {
            return copy[mid];
        }
        return (copy[mid - 1] + copy[mid]) / 2.0;
    }

    public static int percentile(int[] values, int pct) {
        if (values.length == 0 || pct < 0 || pct > 100) {
            throw new IllegalArgumentException("pct");
        }
        int[] copy = Arrays.copyOf(values, values.length);
        Arrays.sort(copy);
        if (pct == 100) {
            return copy[copy.length - 1];
        }
        int rank = (int) Math.round((copy.length - 1) * (pct / 100.0));
        return copy[rank];
    }
}
