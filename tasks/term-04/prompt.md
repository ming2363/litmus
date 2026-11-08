# term-04: 跨时区多服务日志错误峰值分析

## 背景与需求
工作目录的 `logs/` 目录下存放了多份服务日志文件（包含子目录中的 `.log` 文件，如 `logs/archive/*.log`）。不同服务采用了不同的时间戳格式和时区偏移，并且日志中包含多行堆栈跟踪与非错误级别日志。
请递归解析 `logs/` 下的全部 `.log` 文件，按 **UTC 分钟桶** 统计错误数量与峰值，并将结果写入工作目录根下的 `report.json`。

## 解析规则
1. **哪些行是新的日志条目**：只有行首（无前导空白字符）匹配以下任一时间戳加日志级别格式的行，才是一条独立日志记录：
   - ISO-8601 格式：`<YYYY-MM-DDTHH:MM:SS(Z|±HH:MM)> <LEVEL> ...`
   - 方括号格式：`[<YYYY-MM-DD HH:MM:SS ±HHMM>] <LEVEL> ...`
   以空白字符开头、`#` 开头、空行，或行首无时间戳的堆栈续行（如 `Traceback`、`File ...`、`Caused by:`）一律**不得**单独计为日志记录，即使续行内容出现 `ERROR` 或 `FATAL` 字样。
2. **错误级别定义**：仅统计日志级别 `<LEVEL>` 为 `ERROR` 或 `FATAL` 的记录；忽略 `DEBUG`、`INFO`、`WARN`（即使其消息体内含 `ERROR` 字符串）。
3. **时区与分钟桶格式**：将每条错误记录的时间戳统一换算为 UTC 时间，并截断到分钟，格式为 `YYYY-MM-DDTHH:MMZ`（例如 `2026-11-08T14:15:30+08:00` 归入 `2026-11-08T06:15Z`）。

## `report.json` 输出格式
必须为包含且仅包含以下 5 个字段的 JSON 对象：
```json
{
  "total_errors": <整数，所有 .log 文件中的错误记录总数>,
  "peak_minute_utc": "<错误数最多的 UTC 分钟，格式 YYYY-MM-DDTHH:MMZ>",
  "peak_error_count": <整数，峰值分钟的错误数>,
  "by_file": {
    "<相对 logs/ 的路径，如 archive/batch-2026-11.log>": <整数，该文件错误数>
  },
  "top_minutes": [
    {"minute_utc": "<YYYY-MM-DDTHH:MMZ>", "count": <整数>}
  ]
}
```
- `top_minutes` 取错误数最多的前 3 个 UTC 分钟，按 `count` 降序排列（`count` 相同时按 `minute_utc` 字典序升序）。
- `by_file` 必须包含 `logs/` 下所有 `.log` 文件（相对于 `logs/` 的 POSIX 路径）。

## 如何自测
- 在工作目录查看并校对 `report.json` 的 JSON 结构与统计结果，也可执行 `python3 litmus.py check` 检查工作目录无违规符号链接。
