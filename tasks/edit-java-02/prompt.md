# edit-java-02: 仅将指定方法的 null 返回重构为 Optional

## 背景与需求

当前项目位于 `src/com/litmus/config/`，包含配置模型 `ConfigEntry`、配置仓储 `ConfigRepository` 以及三个上层调用类：`ConfigService`、`FeatureFlagResolver` 和 `DeploymentAuditHelper`。

目前 `ConfigRepository.findByKey(String key)` 在键不存在或非法时返回 `null`。请进行小范围精确重构：

1. **仅修改指定方法签名为 `Optional`**：
   - 将 `ConfigRepository.findByKey(String key)` 的返回类型改为 `java.util.Optional<ConfigEntry>`。
   - 当 `key` 为 `null`、空白字符串或不存在于仓储中时，返回 `Optional.empty()`（绝不返回 `null`）；存在时返回 `Optional.of(entry)`。
2. **禁止修改其余方法签名**：
   - `ConfigRepository.findRawValue(String key)` 必须保持返回 `String`（找不到时仍返回 `null`）。
   - `ConfigRepository.findParentGroup(String key)` 必须保持返回 `String`（找不到或无所属组时仍返回 `null`）。
   - `ConfigService.findOverrideOrNull(String key)` 及 `ConfigService`、`FeatureFlagResolver`、`DeploymentAuditHelper` 中所有公开方法签名均不得改变。
3. **同步更新全部内部调用点**：
   - 同步修改 `ConfigService`、`FeatureFlagResolver`、`DeploymentAuditHelper` 中对 `ConfigRepository.findByKey(...)` 的调用处，保证整个模块按 `Optional<ConfigEntry>` 语义正确工作并维持所有既有行为。

## 约束条件

- 只允许修改 `ConfigRepository.java`、`ConfigService.java`、`FeatureFlagResolver.java`、`DeploymentAuditHelper.java`。
- **改动行数上限 (`max_changed_lines`)：`45` 行**。
- 不得修改 `ConfigEntry.java` 或可见测试文件 `ConfigPublicTest.java`。
- 仅使用 JDK 17 标准库，无第三方依赖；全部文件 UTF-8 编码、LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
