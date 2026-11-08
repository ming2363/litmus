package metering;

public class TierPublicTest {

    public void testExactMiddle() {
        long[] values = {1L, 3L, 5L, 8L};
        eq(TierIndex.floorIndex(values, 5L), 2, "命中中间唯一元素");
    }

    public void testExactEnds() {
        long[] values = {2L, 4L, 6L};
        eq(TierIndex.floorIndex(values, 2L), 0, "命中第一个");
        eq(TierIndex.floorIndex(values, 6L), 2, "命中最后一个");
    }

    public void testSingleEqual() {
        eq(TierIndex.floorIndex(new long[] {7L}, 7L), 0, "单元素命中");
    }

    public void testNullArray() {
        try {
            TierIndex.floorIndex(null, 1L);
            throw new AssertionError("null 数组应抛出空指针");
        } catch (NullPointerException expected) {
            // 预期异常
        }
    }

    public void testTariffRejectsBadShape() {
        try {
            new TariffPlan(new long[] {}, new long[] {});
            throw new AssertionError("空档位应被拒绝");
        } catch (IllegalArgumentException expected) {
            // 预期异常
        }
        try {
            new TariffPlan(new long[] {0L, 10L}, new long[] {1L});
            throw new AssertionError("长度不一致应被拒绝");
        } catch (IllegalArgumentException expected) {
            // 预期异常
        }
        try {
            new TariffPlan(new long[] {0L, 0L}, new long[] {1L, 2L});
            throw new AssertionError("非严格递增应被拒绝");
        } catch (IllegalArgumentException expected) {
            // 预期异常
        }
    }

    public void testQuoteAtExactThreshold() {
        TariffPlan plan = new TariffPlan(new long[] {0L, 100L, 200L}, new long[] {10L, 8L, 5L});
        BillDraft bill = BillDraft.quote(plan, 100L);
        eq(bill.unitPriceFen, 8L, "正好落在第二档起点");
        eq(bill.amountFen, 800L, "金额");
        eq(plan.unitPrice(0L), 10L, "最低档起点");
        eq(plan.unitPrice(200L), 5L, "最高档起点");
    }

    public void testLastDuplicate() {
        long[] values = {1L, 2L, 2L, 2L, 3L};
        eq(TierIndex.floorIndex(values, 2L), 3, "重复值应取最后一个");
    }

    private static void eq(long actual, long expected, String label) {
        if (actual != expected) {
            throw new AssertionError(label + "，期望 " + expected + " 实际 " + actual);
        }
    }
}
