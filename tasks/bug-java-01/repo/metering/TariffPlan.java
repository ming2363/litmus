package metering;

/**
 * 按档位起点选择单价。档位起点严格递增。
 */
public final class TariffPlan {

    private final long[] thresholds;
    private final long[] unitPriceFen;

    public TariffPlan(long[] thresholds, long[] unitPriceFen) {
        if (thresholds == null || unitPriceFen == null) {
            throw new NullPointerException("档位");
        }
        if (thresholds.length == 0 || thresholds.length != unitPriceFen.length) {
            throw new IllegalArgumentException("档位和单价必须等长且不能为空");
        }
        for (int i = 1; i < thresholds.length; i++) {
            if (thresholds[i] <= thresholds[i - 1]) {
                throw new IllegalArgumentException("档位起点必须严格递增");
            }
        }
        this.thresholds = thresholds.clone();
        this.unitPriceFen = unitPriceFen.clone();
    }

    public int tierCount() {
        return thresholds.length;
    }

    public long thresholdAt(int index) {
        return thresholds[index];
    }

    public long unitPrice(long usage) {
        int index = TierIndex.floorIndex(thresholds, usage);
        if (index < 0 || index >= thresholds.length) {
            throw new IllegalArgumentException("用量低于最低档: " + usage);
        }
        return unitPriceFen[index];
    }
}
