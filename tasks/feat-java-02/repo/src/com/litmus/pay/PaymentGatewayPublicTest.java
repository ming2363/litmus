package com.litmus.pay;

public class PaymentGatewayPublicTest {

    private static void assertEq(Object expected, Object actual, String msg) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new AssertionError(msg + " (expected=" + expected + ", actual=" + actual + ")");
        }
    }

    public void testExistingChannelsBehavior() {
        PaymentGateway gw = new PaymentGateway();

        PaymentReceipt r1 = gw.process(new PaymentRequest("O-1", PaymentChannel.CARD, 10_000L, "USD"));
        assertEq(320L, r1.getFeeCents(), "CARD fee");
        assertEq(9_680L, r1.getNetCents(), "CARD net");
        assertEq("CARD-O-1-USD", r1.getReferenceCode(), "CARD ref");

        PaymentReceipt r2 = gw.process(new PaymentRequest("O-2", PaymentChannel.BANK_TRANSFER, 100_000L, "EUR"));
        assertEq(200L, r2.getFeeCents(), "BANK min fee");
        assertEq("WIRE-O-2-EUR", r2.getReferenceCode(), "BANK ref");

        PaymentReceipt r3 = gw.process(new PaymentRequest("O-3", PaymentChannel.E_WALLET, 1_000L, "SGD"));
        assertEq(15L, r3.getFeeCents(), "WALLET fee");
        assertEq("WALLET-O-3-SGD", r3.getReferenceCode(), "WALLET ref");
    }

    public void testRiskValidationRejectsUnsupportedCurrency() {
        PaymentGateway gw = new PaymentGateway();
        boolean threw = false;
        try {
            gw.process(new PaymentRequest("O-4", PaymentChannel.BANK_TRANSFER, 50_000L, "GBP"));
        } catch (IllegalArgumentException expected) {
            threw = true;
        }
        if (!threw) {
            throw new AssertionError("BANK_TRANSFER 不应支持 GBP");
        }
    }
}
