package com.litmus.order;

import java.util.ArrayList;
import java.util.List;

/**
 * 履约订单业务校验器。
 */
public class OrderValidator {

    public ValidationResult validate(Order order) {
        List<String> codes = new ArrayList<>();
        List<String> messages = new ArrayList<>();

        if (order == null) {
            codes.add("ORDER_NULL");
            messages.add("订单对象不能为空");
            return new ValidationResult(codes, messages);
        }

        if (order.getOrderId() == null || order.getOrderId().isBlank()) {
            codes.add("ORDER_ID_REQUIRED");
            messages.add("订单号不能为空");
        }

        if (order.getItems().isEmpty()) {
            codes.add("ITEMS_EMPTY");
            messages.add("订单明细不能为空");
        }

        if (!ShippingPolicy.isValidShippingMethod(order.getShippingMethod())) {
            codes.add("SHIPPING_METHOD_INVALID");
            messages.add("不支持的配送方式: " + order.getShippingMethod());
        }

        if (!ShippingPolicy.isSupportedRegion(order.getRegionCode())) {
            codes.add("REGION_UNSUPPORTED");
            messages.add("不支持的收货区域: " + order.getRegionCode());
        }

        long totalCents = 0L;
        for (OrderItem item : order.getItems()) {
            if (item.getSku() == null || item.getSku().isBlank()) {
                codes.add("ITEM_SKU_REQUIRED");
                messages.add("商品 SKU 不能为空");
                break;
            }
            if (item.getQuantity() <= 0) {
                codes.add("ITEM_QUANTITY_INVALID");
                messages.add("商品数量必须大于 0: " + item.getSku());
                break;
            }
            if (item.getUnitPriceCents() < 0) {
                codes.add("ITEM_PRICE_INVALID");
                messages.add("商品单价不能为负: " + item.getSku());
                break;
            }
            totalCents += item.lineTotalCents();
        }

        long limit = ShippingPolicy.maxOrderAmountCents(order.getCustomerTier());
        if (totalCents > limit) {
            codes.add("ORDER_AMOUNT_EXCEEDED");
            messages.add("订单总额超过等级上限");
        }

        return new ValidationResult(codes, messages);
    }
}
