# tool-04: 相对日期换算与工具调用

## 背景与基准日期
**假设“今天”的日期固定为 `2026-11-08`（星期日）。**
请阅读工作目录下的 `schedule_request.md`，把其中的全部相对日期和日历描述准确换算为 `YYYY-MM-DD` 格式，并按请求顺序生成工具调用列表写入 `answer.json`。

## 工具定义（JSON Schema）
```json
[
  {
    "name": "query_blackout_windows",
    "description": "查询给定闭区间日期内的发布冻结窗口",
    "parameters": {
      "type": "object",
      "properties": {
        "start_date": {
          "type": "string",
          "description": "起始日期，格式 YYYY-MM-DD"
        },
        "end_date": {
          "type": "string",
          "description": "结束日期，格式 YYYY-MM-DD"
        }
      },
      "required": [
        "start_date",
        "end_date"
      ]
    }
  },
  {
    "name": "schedule_maintenance",
    "description": "预约集群维护窗口及备用演练日期",
    "parameters": {
      "type": "object",
      "properties": {
        "cluster": {
          "type": "string",
          "description": "目标集群名"
        },
        "target_date": {
          "type": "string",
          "description": "正式维护日期，格式 YYYY-MM-DD"
        },
        "backup_date": {
          "type": "string",
          "description": "备用回滚演练日期，格式 YYYY-MM-DD"
        }
      },
      "required": [
        "cluster",
        "target_date",
        "backup_date"
      ]
    }
  },
  {
    "name": "cancel_maintenance",
    "description": "取消已预约的集群维护",
    "parameters": {
      "type": "object",
      "properties": {
        "maintenance_id": {
          "type": "string"
        }
      },
      "required": [
        "maintenance_id"
      ]
    }
  }
]
```

## 答案格式与约束
- `answer.json` 必须为有序 JSON 数组：`[{"name": ..., "args": {...}}, ...]`。
- 日期参数必须为 `YYYY-MM-DD` 格式字符串；只传 schema 规定的必填参数。

## 如何自测
- 执行 `python3 litmus.py check` 校验 `answer.json` 的 JSON 结构是否合法（不判对错）。
