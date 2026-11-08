package com.litmus.config;

import java.util.Objects;

/**
 * 配置读取与类型转换服务。
 */
public final class ConfigService {
    private final ConfigRepository repository;

    public ConfigService(ConfigRepository repository) {
        this.repository = Objects.requireNonNull(repository, "repository 不能为空");
    }

    public String resolveString(String key, String defaultValue) {
        ConfigEntry entry = repository.findByKey(key);
        if (entry == null || entry.rawValue() == null || entry.rawValue().trim().isEmpty()) {
            return defaultValue;
        }
        return entry.rawValue().trim();
    }

    public int resolveInt(String key, int defaultValue) {
        ConfigEntry entry = repository.findByKey(key);
        if (entry == null || entry.rawValue() == null) {
            return defaultValue;
        }
        try {
            return Integer.parseInt(entry.rawValue().trim());
        } catch (NumberFormatException ex) {
            return defaultValue;
        }
    }

    public String describeEntry(String key) {
        ConfigEntry entry = repository.findByKey(key);
        if (entry == null) {
            return "MISSING:" + key;
        }
        String group = entry.parentGroup() == null ? "default" : entry.parentGroup();
        String status = entry.deprecated() ? "DEPRECATED" : "ACTIVE";
        return entry.key() + "[" + group + ":" + status + "]=" + entry.rawValue();
    }

    /**
     * 查找非弃用的覆盖配置值，找不到或已弃用时返回 null。
     */
    public String findOverrideOrNull(String key) {
        String val = repository.findRawValue(key);
        if (val == null || val.trim().isEmpty()) {
            return null;
        }
        return val.trim();
    }
}
