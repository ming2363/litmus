package com.litmus.pay;

/**
 * 支付手续费计算器（当前使用 switch 按渠道分支）。
 */
public class FeeCalculator {

    public long calculateFee(PaymentChannel channel, long amountCents, String currency) {
        if (channel == null) {
            throw new IllegalArgumentException("支付渠道不能为空");
        }
        if (amountCents <= 0) {
            throw new IllegalArgumentException("交易金额必须大于 0");
        }
        if (currency == null || currency.isBlank()) {
            throw new IllegalArgumentException("币种不能为空");
        }
        switch (channel) {
            case CARD:
                return Math.max(30L, (amountCents * 29L) / 1000L + 30L);
            case BANK_TRANSFER:
                return Math.min(2500L, Math.max(200L, amountCents / 1000L));
            case E_WALLET:
                return Math.max(10L, (amountCents * 15L) / 1000L);
            default:
                throw new IllegalArgumentException("不支持的渠道: " + channel);
        }
    }
}
