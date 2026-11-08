package settlement;

import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * 按渠道费率从金额（分）计算手续费（分）。
 */
public final class ChannelFee {

    private ChannelFee() {
    }

    public static long feeFen(long amountFen, BigDecimal rate) {
        if (rate == null) {
            throw new NullPointerException("rate");
        }
        if (amountFen < 0 || rate.signum() < 0) {
            throw new IllegalArgumentException("金额和费率不能为负");
        }
        BigDecimal raw = BigDecimal.valueOf(amountFen).multiply(rate);
        // 向零截断到分。半分不会进位。
        return raw.setScale(0, RoundingMode.DOWN).longValueExact();
    }
}
