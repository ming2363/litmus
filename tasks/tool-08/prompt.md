# tool-08: 复杂工具集选型与严格枚举参数映射

## 背景与需求
工作目录下提供了：
- `tools_schema.json`：包含 26 个相似运维/观测/FinOps 工具的完整 JSON Schema 定义；
- `service_registry.json`：服务资产、区域与成本中心映射台账；
- `change_request.md`：本次需要完成的三项运维与预算变更诉求。

请精确阅读全部三个文件，选出对应的 3 个正确工具，并将业务描述严格映射为 schema 允许的**精确枚举字符串与数据类型**，写入工作目录根下的 `answer.json`（三项操作无先后依赖，判分按集合匹配，但对工具名、参数名、严格枚举值大小写与格式做**零容差**精确比对）。

## 答案格式与约束
- `answer.json` 必须为 JSON 数组：`[{"name": ..., "args": {...}}, ...]`。
- 严格传入各选中工具 `required` 定义的参数，禁止多余字段或 `null`。

## 如何自测
- 执行 `python3 litmus.py check` 校验 `answer.json` 的 JSON 结构是否合法（不判对错）。
