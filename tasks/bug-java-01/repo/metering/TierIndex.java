package metering;

/**
 * 在非递减数组里定位用量所属的档位。
 */
public final class TierIndex {

    private TierIndex() {
    }

    /**
     * 返回目标在有序数组中的位置。
     * 当前实现停在第一个大于等于目标的下标，数组尾部之外则返回长度。
     */
    public static int floorIndex(long[] values, long target) {
        if (values == null) {
            throw new NullPointerException("values");
        }
        int low = 0;
        int high = values.length;
        while (low < high) {
            int mid = (low + high) >>> 1;
            if (values[mid] < target) {
                low = mid + 1;
            } else {
                high = mid;
            }
        }
        return low;
    }
}
