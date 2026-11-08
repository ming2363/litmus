package com.litmus.config;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 内存配置条目仓储。
 */
public final class ConfigRepository {
    private final Map<String, ConfigEntry> entries = new LinkedHashMap<>();

    public void put(ConfigEntry entry) {
        if (entry == null) {
            throw new IllegalArgumentException("entry 不能为空");
        }
        entries.put(entry.key(), entry);
    }

    /**
     * 按配置键查询完整配置条目，不存在时返回 null。
     */
    public ConfigEntry findByKey(String key) {
        if (key == null || key.trim().isEmpty()) {
            return null;
        }
        return entries.get(key.trim());
    }

    /**
     * 仅返回原始配置值，不存在时返回 null（保持返回 String）。
     */
    public String findRawValue(String key) {
        if (key == null || key.trim().isEmpty()) {
            return null;
        }
        ConfigEntry entry = entries.get(key.trim());
        return entry == null ? null : entry.rawValue();
    }

    /**
     * 查询配置项所属分组，不存在或未归组时返回 null（保持返回 String）。
     */
    public String findParentGroup(String key) {
        if (key == null || key.trim().isEmpty()) {
            return null;
        }
        ConfigEntry entry = entries.get(key.trim());
        return entry == null ? null : entry.parentGroup();
    }

    public Map<String, ConfigEntry> listByGroup(String group) {
        if (group == null) {
            return Collections.emptyMap();
        }
        Map<String, ConfigEntry> result = new LinkedHashMap<>();
        for (ConfigEntry entry : entries.values()) {
            if (group.equals(entry.parentGroup())) {
                result.put(entry.key(), entry);
            }
        }
        return Collections.unmodifiableMap(result);
    }
}
