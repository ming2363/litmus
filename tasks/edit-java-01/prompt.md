# edit-java-01: 调整审计日志输出为标准单行管道格式

## 背景与需求

当前项目位于 `src/com/litmus/log/`，包含 `LogLevel.java`、`LogRecord.java` 和 `AuditLogger.java`。目前 `AuditLogger.format(LogRecord)` 输出旧版括号格式，不利于日志采集器按列解析且无法处理消息换行。

请仅修改 `src/com/litmus/log/AuditLogger.java`，将 `format(LogRecord record)` 的输出格式调整为以下单行管道分隔格式：

```text
<ISO_INSTANT> | <LEVEL> | <component> | <escapedMessage>
```

具体规则如下：

1. **时间戳 `<ISO_INSTANT>`**：使用 `DateTimeFormatter.ISO_INSTANT.format(record.timestamp())`（与 `Instant.toString()` 等价的 UTC ISO-8601 格式）。
2. **日志级别 `<LEVEL>`**：使用大写级别名 `record.level().name()`（`INFO`、`WARN`、`ERROR`）。
3. **组件名 `<component>`**：对 `record.component()` 去除首尾空白；若为 `null` 或去除空白后为空串，统一输出 `"core"`。
4. **单行消息 `<escapedMessage>`**：若 `record.message()` 为 `null`，输出空字符串 `""`；否则依次将 `\r\n`、`\r`、`\n` 转义为字面量 `\n`（即两个字符 `\` 和 `n`），确保单条日志严格占一行。
5. **分隔符**：固定为 `" | "`（竖线两侧各一个半角空格）。
6. **`record == null` 校验**：保持原有 `IllegalArgumentException` 校验不变；`write(LogRecord record, List<String> sink)` 继续将 `format(record)` 的结果追加写入 `sink`（`sink == null` 时抛 `IllegalArgumentException`）。

示例：

- 输入：`timestamp=2026-03-10T08:15:30Z`, `level=WARN`, `component=" auth "`, `message="line1\nline2"`
- 输出：`2026-03-10T08:15:30Z | WARN | auth | line1\nline2`

## 约束条件

- 只允许修改 `src/com/litmus/log/AuditLogger.java`。
- **改动行数上限 (`max_changed_lines`)：`18` 行**。
- 不得修改 `LogLevel.java`、`LogRecord.java` 或可见测试文件 `AuditLoggerPublicTest.java`。
- 仅使用 JDK 17 标准库，无第三方依赖；全部文件 UTF-8 编码、LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
