package com.litmus.pay;

/**
 * 支付结算回执模型。
 */
public class PaymentReceipt {
    private final String orderId;
    private final PaymentChannel channel;
    private final long amountCents;
    private final long feeCents;
    private final long netCents;
    private final String currency;
    private final String referenceCode;

    public PaymentReceipt(
            String orderId,
            PaymentChannel channel,
            long amountCents,
            long feeCents,
            String currency,
            String referenceCode) {
        this.orderId = orderId;
        this.channel = channel;
        this.amountCents = amountCents;
        this.feeCents = feeCents;
        this.netCents = amountCents - feeCents;
        this.currency = currency;
        this.referenceCode = referenceCode;
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

    public long getFeeCents() {
        return feeCents;
    }

    public long getNetCents() {
        return netCents;
    }

    public String getCurrency() {
        return currency;
    }

    public String getReferenceCode() {
        return referenceCode;
    }
}
