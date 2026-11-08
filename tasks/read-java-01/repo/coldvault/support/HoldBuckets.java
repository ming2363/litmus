package coldvault.support;

import java.util.LinkedHashMap;
import java.util.Map;

/** 停留时长分桶。 */
public final class HoldBuckets {
    private HoldBuckets() {
    }

    public static String bucketOf(int minutes) {
        if (minutes < 0) {
            throw new IllegalArgumentException("minutes");
        }
        if (minutes < 30) {
            return "le_30";
        }
        if (minutes < 120) {
            return "le_120";
        }
        if (minutes < 480) {
            return "le_480";
        }
        if (minutes < 1440) {
            return "le_1440";
        }
        return "gt_1440";
    }

    public static Map<String, Integer> tally(int[] samples) {
        Map<String, Integer> counts = new LinkedHashMap<String, Integer>();
        counts.put("le_30", Integer.valueOf(0));
        counts.put("le_120", Integer.valueOf(0));
        counts.put("le_480", Integer.valueOf(0));
        counts.put("le_1440", Integer.valueOf(0));
        counts.put("gt_1440", Integer.valueOf(0));
        for (int i = 0; i < samples.length; i++) {
            String name = bucketOf(samples[i]);
            counts.put(name, Integer.valueOf(counts.get(name).intValue() + 1));
        }
        return counts;
    }
}
