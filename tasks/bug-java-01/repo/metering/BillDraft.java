package metering;

/**
 * 一张尚未落账的用量账单。金额等于用量乘以选中档的单价。
 */
public final class BillDraft {

    public final long usage;
    public final long unitPriceFen;
    public final long amountFen;

    public BillDraft(long usage, long unitPriceFen, long amountFen) {
        this.usage = usage;
        this.unitPriceFen = unitPriceFen;
        this.amountFen = amountFen;
    }

    public static BillDraft quote(TariffPlan plan, long usage) {
        if (plan == null) {
            throw new NullPointerException("plan");
        }
        long price = plan.unitPrice(usage);
        long amount = Math.multiplyExact(usage, price);
        return new BillDraft(usage, price, amount);
    }
}
