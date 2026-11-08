package com.litmus.pay;

/**
 * 支付网关处理入口（当前使用 switch 组装渠道参考号）。
 */
public class PaymentGateway {
    private final RiskChecker riskChecker;
    private final FeeCalculator feeCalculator;

    public PaymentGateway() {
        this.riskChecker = new RiskChecker();
        this.feeCalculator = new FeeCalculator();
    }

    public PaymentGateway(RiskChecker riskChecker, FeeCalculator feeCalculator) {
        this.riskChecker = riskChecker;
        this.feeCalculator = feeCalculator;
    }

    public PaymentReceipt process(PaymentRequest request) {
        riskChecker.validate(request);
        long fee = feeCalculator.calculateFee(
                request.getChannel(),
                request.getAmountCents(),
                request.getCurrency()
        );
        String ref;
        switch (request.getChannel()) {
            case CARD:
                ref = "CARD-" + request.getOrderId() + "-" + request.getCurrency();
                break;
            case BANK_TRANSFER:
                ref = "WIRE-" + request.getOrderId() + "-" + request.getCurrency();
                break;
            case E_WALLET:
                ref = "WALLET-" + request.getOrderId() + "-" + request.getCurrency();
                break;
            default:
                throw new IllegalArgumentException("不支持的渠道: " + request.getChannel());
        }
        return new PaymentReceipt(
                request.getOrderId(),
                request.getChannel(),
                request.getAmountCents(),
                fee,
                request.getCurrency(),
                ref
        );
    }
}
