package settlement;

import java.math.BigDecimal;

/**
 * 把一批订单的渠道手续费加总。
 */
public final class Statement {

    private Statement() {
    }

    public static long totalFee(long[] amounts, BigDecimal rate) {
        if (amounts == null) {
            throw new NullPointerException("amounts");
        }
        long total = 0L;
        for (long amount : amounts) {
            total = Math.addExact(total, ChannelFee.feeFen(amount, rate));
        }
        return total;
    }

    public static int size(long[] amounts) {
        if (amounts == null) {
            throw new NullPointerException("amounts");
        }
        return amounts.length;
    }
}
