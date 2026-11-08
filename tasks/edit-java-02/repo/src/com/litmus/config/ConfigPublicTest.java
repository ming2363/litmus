package com.litmus.config;

import java.util.Arrays;
import java.util.Map;

/**
 * 可见配置服务与特性开关测试（通过对外接口验证，兼容重构前后）。
 */
public class ConfigPublicTest {
    private static void assertEquals(Object expected, Object actual, String msg) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new AssertionError(msg + "，期望=" + expected + "，实际=" + actual);
        }
    }

    private ConfigRepository buildSampleRepo() {
        ConfigRepository repo = new ConfigRepository();
        repo.put(new ConfigEntry("db.pool.size", "16", "database", false));
        repo.put(new ConfigEntry("service.name", "order-api", null, false));
        repo.put(new ConfigEntry("legacy.mode", "on", "core", true));
        repo.put(new ConfigEntry("feature.dark_mode", "true", "ui", false));
        repo.put(new ConfigEntry("feature.dark_mode.rollout", "45", "ui", false));
        return repo;
    }

    public void testConfigServiceAndResolverBehavior() {
        ConfigRepository repo = buildSampleRepo();
        ConfigService service = new ConfigService(repo);
        assertEquals("order-api", service.resolveString("service.name", "unknown"), "读取字符串配置失败");
        assertEquals("fallback", service.resolveString("not.found", "fallback"), "缺失键应使用默认值");
        assertEquals(16, service.resolveInt("db.pool.size", 4), "读取整型配置失败");
        assertEquals("db.pool.size[database:ACTIVE]=16", service.describeEntry("db.pool.size"), "describeEntry 失败");
        assertEquals("MISSING:absent", service.describeEntry("absent"), "缺失键 describeEntry 失败");
        assertEquals(null, repo.findParentGroup("service.name"), "无分组应返回 null");
        assertEquals(null, service.findOverrideOrNull("absent"), "缺失覆盖键应返回 null");

        FeatureFlagResolver resolver = new FeatureFlagResolver(repo);
        assertEquals(true, resolver.isEnabled("dark_mode", false), "特性开关读取失败");
        assertEquals(45, resolver.rolloutPercentage("dark_mode"), "灰度比例读取失败");

        DeploymentAuditHelper audit = new DeploymentAuditHelper(repo);
        Map<String, Object> report = audit.summarizeRequiredKeys(Arrays.asList("db.pool.size", "legacy.mode", "absent"));
        assertEquals(false, report.get("ready"), "包含缺失/弃用键时不应 ready");
    }
}
