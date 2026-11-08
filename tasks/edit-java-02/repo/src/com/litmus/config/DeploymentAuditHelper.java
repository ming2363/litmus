package com.litmus.config;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * 发布前必需配置项检查助手。
 */
public final class DeploymentAuditHelper {
    private final ConfigRepository repository;

    public DeploymentAuditHelper(ConfigRepository repository) {
        this.repository = Objects.requireNonNull(repository, "repository 不能为空");
    }

    public Map<String, Object> summarizeRequiredKeys(List<String> requiredKeys) {
        List<String> missing = new ArrayList<>();
        List<String> deprecated = new ArrayList<>();
        Map<String, String> groups = new LinkedHashMap<>();

        for (String key : requiredKeys) {
            ConfigEntry entry = repository.findByKey(key);
            if (entry == null) {
                missing.add(key);
                continue;
            }
            if (entry.deprecated()) {
                deprecated.add(key);
            }
            String parentGroup = repository.findParentGroup(key);
            if (parentGroup != null) {
                groups.put(key, parentGroup);
            }
        }

        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("missing", missing);
        summary.put("deprecated", deprecated);
        summary.put("groups", groups);
        summary.put("ready", missing.isEmpty() && deprecated.isEmpty());
        return summary;
    }
}
