package com.litmus.pay;

/**
 * 支付交易请求模型。
 */
public class PaymentRequest {
    private final String orderId;
    private final PaymentChannel channel;
    private final long amountCents;
    private final String currency;

    public PaymentRequest(String orderId, PaymentChannel channel, long amountCents, String currency) {
        this.orderId = orderId;
        this.channel = channel;
        this.amountCents = amountCents;
        this.currency = currency;
    }

    public String getOrderId() {
        return orderId;
    }

    public PaymentChannel getChannel() {
        return channel;
    }

    public long getAmountCents() {
        return amountCents;
    }

    public String getCurrency() {
        return currency;
    }
}
