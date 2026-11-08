package com.litmus.config;

import java.util.Objects;

/**
 * 特性开关与灰度百分比解析器。
 */
public final class FeatureFlagResolver {
    private static final String PREFIX = "feature.";
    private static final String ROLLOUT_SUFFIX = ".rollout";
    private final ConfigRepository repository;

    public FeatureFlagResolver(ConfigRepository repository) {
        this.repository = Objects.requireNonNull(repository, "repository 不能为空");
    }

    public boolean isEnabled(String flagName, boolean defaultValue) {
        if (flagName == null || flagName.trim().isEmpty()) {
            return defaultValue;
        }
        ConfigEntry entry = repository.findByKey(PREFIX + flagName.trim());
        if (entry == null || entry.deprecated() || entry.rawValue() == null) {
            return defaultValue;
        }
        String v = entry.rawValue().trim();
        if ("true".equalsIgnoreCase(v) || "1".equals(v)) {
            return true;
        }
        if ("false".equalsIgnoreCase(v) || "0".equals(v)) {
            return false;
        }
        return defaultValue;
    }

    public int rolloutPercentage(String flagName) {
        if (flagName == null || flagName.trim().isEmpty()) {
            return 0;
        }
        ConfigEntry entry = repository.findByKey(PREFIX + flagName.trim() + ROLLOUT_SUFFIX);
        if (entry == null || entry.deprecated() || entry.rawValue() == null) {
            return 0;
        }
        try {
            int pct = Integer.parseInt(entry.rawValue().trim());
            return Math.max(0, Math.min(100, pct));
        } catch (NumberFormatException ex) {
            return 0;
        }
    }
}
