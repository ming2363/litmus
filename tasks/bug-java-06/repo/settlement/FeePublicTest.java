package settlement;

import java.math.BigDecimal;

public class FeePublicTest {

    public void testExactRate() {
        eq(ChannelFee.feeFen(10000L, new BigDecimal("0.006")), 60L, "整数分");
        eq(ChannelFee.feeFen(0L, new BigDecimal("0.006")), 0L, "零金额");
        eq(ChannelFee.feeFen(100L, BigDecimal.ZERO), 0L, "零费率");
        eq(ChannelFee.feeFen(100L, new BigDecimal("0.10")), 10L, "一位小数也能除尽");
    }

    public void testRejectsNegativeAndNull() {
        try {
            ChannelFee.feeFen(1L, null);
            throw new AssertionError("费率为空应抛出空指针");
        } catch (NullPointerException expected) {
            // 预期异常
        }
        try {
            ChannelFee.feeFen(-1L, new BigDecimal("0.01"));
            throw new AssertionError("负金额应被拒绝");
        } catch (IllegalArgumentException ex) {
            if (ex.getMessage() == null || !ex.getMessage().contains("不能为负")) {
                throw new AssertionError("负金额的消息不正确");
            }
        }
        try {
            ChannelFee.feeFen(1L, new BigDecimal("-0.01"));
            throw new AssertionError("负费率应被拒绝");
        } catch (IllegalArgumentException ex) {
            if (ex.getMessage() == null || !ex.getMessage().contains("不能为负")) {
                throw new AssertionError("负费率的消息不正确");
            }
        }
    }

    public void testStatementSumsExactFees() {
        long[] amounts = {10000L, 0L, 200L};
        eq(Statement.totalFee(amounts, new BigDecimal("0.006")), 61L, "合计");
        eq(Statement.totalFee(new long[] {}, new BigDecimal("0.006")), 0L, "空批次");
        eq(Reconciliation.differenceFen(amounts, new BigDecimal("0.006"), 61L), 0L, "已对齐");
    }

    public void testHalfRoundsAwayFromZero() {
        eq(ChannelFee.feeFen(250L, new BigDecimal("0.006")), 2L, "1.5 分应进成 2");
        eq(ChannelFee.feeFen(5L, new BigDecimal("0.5")), 3L, "2.5 分应进成 3");
    }

    private static void eq(long actual, long expected, String label) {
        if (actual != expected) {
            throw new AssertionError(label + "，期望 " + expected + " 实际 " + actual);
        }
    }
}
