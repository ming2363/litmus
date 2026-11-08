package com.litmus.pay;

import java.util.Set;

/**
 * 支付风控与限额校验器（当前使用 switch 按渠道分支）。
 */
public class RiskChecker {
    private static final Set<String> CARD_CURRENCIES = Set.of("USD", "EUR", "GBP");
    private static final Set<String> BANK_CURRENCIES = Set.of("USD", "EUR");
    private static final Set<String> WALLET_CURRENCIES = Set.of("USD", "EUR", "SGD");

    public void validate(PaymentRequest request) {
        if (request == null) {
            throw new IllegalArgumentException("支付请求不能为空");
        }
        if (request.getOrderId() == null || request.getOrderId().isBlank()) {
            throw new IllegalArgumentException("订单号不能为空");
        }
        if (request.getChannel() == null) {
            throw new IllegalArgumentException("支付渠道不能为空");
        }
        if (request.getCurrency() == null || request.getCurrency().isBlank()) {
            throw new IllegalArgumentException("币种不能为空");
        }
        long amount = request.getAmountCents();
        String cur = request.getCurrency();
        switch (request.getChannel()) {
            case CARD:
                if (!CARD_CURRENCIES.contains(cur)) {
                    throw new IllegalArgumentException("CARD 不支持币种: " + cur);
                }
                if (amount < 100L || amount > 1_000_000L) {
                    throw new IllegalArgumentException("CARD 金额超出范围 [100, 1000000]: " + amount);
                }
                break;
            case BANK_TRANSFER:
                if (!BANK_CURRENCIES.contains(cur)) {
                    throw new IllegalArgumentException("BANK_TRANSFER 不支持币种: " + cur);
                }
                if (amount < 10_000L || amount > 10_000_000L) {
                    throw new IllegalArgumentException("BANK_TRANSFER 金额超出范围 [10000, 10000000]: " + amount);
                }
                break;
            case E_WALLET:
                if (!WALLET_CURRENCIES.contains(cur)) {
                    throw new IllegalArgumentException("E_WALLET 不支持币种: " + cur);
                }
                if (amount < 50L || amount > 200_000L) {
                    throw new IllegalArgumentException("E_WALLET 金额超出范围 [50, 200000]: " + amount);
                }
                break;
            default:
                throw new IllegalArgumentException("不支持的渠道: " + request.getChannel());
        }
    }
}
