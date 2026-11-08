package com.litmus.order;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 待校验的履约订单对象。
 */
public class Order {
    // 订单唯一编号
    private final String orderId;
    // 客户等级：STANDARD / VIP
    private final String customerTier;
    // 配送方式：STANDARD / ECONOMY / SAME_DAY / COLD_EXPRESS
    private final String shippingMethod;
    // 收货区域编码：NORTH / EAST / SOUTH / WEST / REMOTE
    private final String regionCode;
    // 订单明细列表
    private final List<OrderItem> items;

    public Order(
            String orderId,
            String customerTier,
            String shippingMethod,
            String regionCode,
            List<OrderItem> items) {
        this.orderId = orderId;
        this.customerTier = customerTier;
        this.shippingMethod = shippingMethod;
        this.regionCode = regionCode;
        this.items = items == null
                ? Collections.emptyList()
                : Collections.unmodifiableList(new ArrayList<>(items));
    }

    public String getOrderId() {
        return orderId;
    }

    public String getCustomerTier() {
        return customerTier;
    }

    public String getShippingMethod() {
        return shippingMethod;
    }

    public String getRegionCode() {
        return regionCode;
    }

    public List<OrderItem> getItems() {
        return items;
    }
}
