package settlement;

import java.math.BigDecimal;

/**
 * 我方手续费合计与渠道结算额的差额。正数表示我方算得更多。
 */
public final class Reconciliation {

    private Reconciliation() {
    }

    public static long differenceFen(long[] amounts, BigDecimal rate, long settledFeeFen) {
        return Math.subtractExact(Statement.totalFee(amounts, rate), settledFeeFen);
    }

    public static boolean aligned(long[] amounts, BigDecimal rate, long settledFeeFen) {
        return differenceFen(amounts, rate, settledFeeFen) == 0L;
    }
}
