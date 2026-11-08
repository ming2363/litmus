package com.litmus.pay;

/**
 * 支付渠道枚举。
 */
public enum PaymentChannel {
    CARD,
    BANK_TRANSFER,
    E_WALLET;

    public static PaymentChannel fromCode(String code) {
        if (code == null || code.isBlank()) {
            throw new IllegalArgumentException("支付渠道编码不能为空");
        }
        for (PaymentChannel ch : values()) {
            if (ch.name().equalsIgnoreCase(code.trim())) {
                return ch;
            }
        }
        throw new IllegalArgumentException("未知支付渠道: " + code);
    }
}
