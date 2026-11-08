package com.litmus.order;

import java.util.Set;

/**
 * 配送方式与区域策略配置。
 */
public final class ShippingPolicy {
    private static final Set<String> SUPPORTED_METHODS = Set.of(
            "STANDARD", "ECONOMY", "SAME_DAY", "COLD_EXPRESS"
    );
    private static final Set<String> SUPPORTED_REGIONS = Set.of(
            "NORTH", "EAST", "SOUTH", "WEST", "REMOTE"
    );

    private ShippingPolicy() {
    }

    public static boolean isValidShippingMethod(String shippingMethod) {
        return shippingMethod != null && SUPPORTED_METHODS.contains(shippingMethod);
    }

    public static boolean isSupportedRegion(String regionCode) {
        return regionCode != null && SUPPORTED_REGIONS.contains(regionCode);
    }

    public static long maxOrderAmountCents(String customerTier) {
        if ("VIP".equals(customerTier)) {
            return 5_000_000L;
        }
        return 1_000_000L;
    }

    // 起始桩方法：尚未实现冷链配送方式限制
    public static boolean supportsColdChainMethod(String shippingMethod) {
        return true;
    }

    // 起始桩方法：尚未实现冷链区域限制
    public static boolean supportsColdChainRegion(String regionCode) {
        return true;
    }
}
