package com.litmus.order;

import java.util.List;

public class OrderValidatorPublicTest {

    private static void assertTrue(boolean cond, String msg) {
        if (!cond) {
            throw new AssertionError(msg);
        }
    }

    public void testStandardOrderPasses() {
        OrderValidator validator = new OrderValidator();
        Order order = new Order(
                "ORD-1001",
                "STANDARD",
                "STANDARD",
                "REMOTE",
                List.of(new OrderItem("SKU-01", 2, 1500L, false))
        );
        ValidationResult res = validator.validate(order);
        assertTrue(res.isValid(), "普通商品标准配送应该通过");
    }

    public void testInvalidQuantityAndEmptyOrderFail() {
        OrderValidator validator = new OrderValidator();
        Order empty = new Order("ORD-1002", "VIP", "ECONOMY", "EAST", List.of());
        ValidationResult res1 = validator.validate(empty);
        assertTrue(!res1.isValid(), "空订单应校验失败");
        assertTrue(res1.getErrorCodes().contains("ITEMS_EMPTY"), "应包含 ITEMS_EMPTY");

        Order badQty = new Order(
                "ORD-1003",
                "STANDARD",
                "STANDARD",
                "NORTH",
                List.of(new OrderItem("SKU-02", 0, 500L, false))
        );
        ValidationResult res2 = validator.validate(badQty);
        assertTrue(!res2.isValid(), "数量为 0 应校验失败");
        assertTrue(res2.getErrorCodes().contains("ITEM_QUANTITY_INVALID"), "应包含 ITEM_QUANTITY_INVALID");
    }
}
