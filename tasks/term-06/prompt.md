# term-06: 批量 INI 配置迁移 JSON 与校验

## 背景与需求
工作目录的 `configs/` 目录下存放了若干遗留的 `.ini` 服务配置文件（部分配置存在默认值缺失、类型需要转换或字段违规的问题）。
请按照下方迁移与校验规则，将**校验通过**的 `.ini` 迁移为 JSON 文件写入 `migrated/` 目录，并将整体迁移与错误报告写入工作目录根下的 `migration_report.json`。

## 解析与校验规则
1. 采用标准 INI 语法解析（支持 `#` 与 `;` 注释，支持 `[DEFAULT]` 节；键名按小写处理）。
2. **必填节**：必须同时存在 `[service]` 与 `[runtime]`；`[limits]` 与 `[features]` 为可选节。
3. **`[service]` 字段规则**：
   - `name`（必填，字符串）：非空且仅允许小写字母、数字和连字符（`[a-z0-9-]+`）。
   - `port`（必填，整数）：必须在 `1024` 到 `65535` 之间（含边界）。
   - `tier`（可选，默认 `"standard"`）：仅允许 `"core"`、`"standard"`、`"edge"`。
4. **`[runtime]` 字段规则**：
   - `workers`（可选，默认 `4`，整数）：必须在 `1` 到 `64` 之间（含边界）。
   - `timeout_ms`（可选，默认 `3000`，整数）：必须 `>= 100`。
   - `tls_enabled`（可选，默认 `false`，布尔值）：仅接受大小写不敏感的 `true`/`yes`/`1`（转为 `true`）或 `false`/`no`/`0`（转为 `false`），其他值判为非法。
   - `allowed_origins`（可选，默认 `[]`，字符串数组）：按逗号 `,` 拆分，逐项去首尾空白并忽略空字符串。
5. **`[limits]` 字段规则**（若省略整个节，按默认值补全）：
   - `max_concurrency`（可选，默认 `128`，整数）：必须 `>= runtime.workers`（跨字段校验）。
   - `rate_limit_rps`（可选，默认 `100`，整数）：必须 `> 0`。
6. **`[features]` 字段规则**（若省略整个节，默认 `{}`）：
   - 将 `[features]` 节中**显式声明**的每个键值对转换为布尔值（使用与 `tls_enabled` 相同的布尔转换规则）。
   - **重要**：`[DEFAULT]` 中的键只作为 `[service]`、`[runtime]`、`[limits]` 同名字段的默认值回退，**不得**作为特征开关混入 `features` 对象中。

## 输出格式要求
1. **校验通过的文件**（`<stem>.ini`）：
   - 写入 `migrated/<stem>.json`，不得为校验失败的文件创建 JSON。
   - 每个 JSON 必须为包含且仅包含 `service`、`runtime`、`limits`、`features` 四个键的对象：
     ```json
     {
       "service": {"name": "...", "port": 8080, "tier": "..."},
       "runtime": {"workers": 4, "timeout_ms": 3000, "tls_enabled": false, "allowed_origins": []},
       "limits": {"max_concurrency": 128, "rate_limit_rps": 100},
       "features": {"flag": true}
     }
     ```
2. **迁移汇总报告 `migration_report.json`**（位于工作目录根下）：
   ```json
   {
     "valid_files": ["api-gateway.ini", "..."],
     "invalid_files": [
       {"file": "broken-limits.ini", "errors": ["错误描述1", "..."]}
     ],
     "valid_count": 6,
     "invalid_count": 2
   }
   ```
   - `valid_files` 为通过校验的 `.ini` 文件名（不含目录前缀），按字典序升序。
   - `invalid_files` 按 `file` 字段（文件名）字典序升序，每项的 `errors` 必须是非空字符串数组（错误文案不限，但必须列出触发了校验失败的文件）。

## 如何自测
- 检查 `migrated/` 目录下的文件清单与字段类型，核对 `migration_report.json` 中的计数和文件名。
- 完成后可执行 `python3 litmus.py check` 检查工作目录无违规符号链接。
