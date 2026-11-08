package com.litmus.order;

/**
 * 订单商品明细实体。
 */
public class OrderItem {
    // 商品 SKU 编码
    private final String sku;
    // 购买数量
    private final int quantity;
    // 单价（单位：分）
    private final long unitPriceCents;
    // 是否需要冷链运输
    private final boolean coldChain;

    public OrderItem(String sku, int quantity, long unitPriceCents, boolean coldChain) {
        this.sku = sku;
        this.quantity = quantity;
        this.unitPriceCents = unitPriceCents;
        this.coldChain = coldChain;
    }

    public String getSku() {
        return sku;
    }

    public int getQuantity() {
        return quantity;
    }

    public long getUnitPriceCents() {
        return unitPriceCents;
    }

    public boolean isColdChain() {
        return coldChain;
    }

    public long lineTotalCents() {
        return (long) quantity * unitPriceCents;
    }
}
