package com.litmus.config;

import java.util.Objects;

/**
 * 不可变配置条目。
 */
public final class ConfigEntry {
    private final String key;
    private final String rawValue;
    private final String parentGroup;
    private final boolean deprecated;

    public ConfigEntry(String key, String rawValue, String parentGroup, boolean deprecated) {
        this.key = Objects.requireNonNull(key, "key 不能为空");
        this.rawValue = rawValue;
        this.parentGroup = parentGroup;
        this.deprecated = deprecated;
    }

    public String key() {
        return key;
    }

    public String rawValue() {
        return rawValue;
    }

    public String parentGroup() {
        return parentGroup;
    }

    public boolean deprecated() {
        return deprecated;
    }
}
