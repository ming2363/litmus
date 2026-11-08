# tool-05: 多项独立发布前检查（无序集合调用）

## 背景与需求
请结合工作目录下的 `preflight.md` 与 `status_board.json`，识别当前**仍待完成**（`status` 不为 `"completed"`）的发布准备任务，并输出所有需要触发的工具调用到 `answer.json`。
各项待办操作之间相互独立、顺序任意（判分按无序集合匹配），但**不得**重复触发状态已为 `"completed"` 或已取消的任务，也不得漏掉待完成项。

## 工具定义（JSON Schema）
```json
[
  {
    "name": "warm_edge_cache",
    "description": "预热指定区域边缘节点的命名空间缓存",
    "parameters": {
      "type": "object",
      "properties": {
        "region": {
          "type": "string"
        },
        "namespace": {
          "type": "string"
        }
      },
      "required": [
        "region",
        "namespace"
      ]
    }
  },
  {
    "name": "verify_dns_propagation",
    "description": "校验域名的指定 DNS 记录是否已全网生效",
    "parameters": {
      "type": "object",
      "properties": {
        "hostname": {
          "type": "string"
        },
        "record_type": {
          "type": "string",
          "enum": [
            "A",
            "AAAA",
            "CNAME",
            "TXT"
          ]
        }
      },
      "required": [
        "hostname",
        "record_type"
      ]
    }
  },
  {
    "name": "sync_feature_flags",
    "description": "把指定服务在目标环境下的特性开关同步至全量实例",
    "parameters": {
      "type": "object",
      "properties": {
        "service": {
          "type": "string"
        },
        "environment": {
          "type": "string",
          "enum": [
            "staging",
            "prod"
          ]
        }
      },
      "required": [
        "service",
        "environment"
      ]
    }
  },
  {
    "name": "purge_edge_cache",
    "description": "清空指定区域的边缘缓存",
    "parameters": {
      "type": "object",
      "properties": {
        "region": {
          "type": "string"
        },
        "namespace": {
          "type": "string"
        }
      },
      "required": [
        "region",
        "namespace"
      ]
    }
  }
]
```

## 答案格式与约束
- `answer.json` 必须为 JSON 数组：`[{"name": ..., "args": {...}}, ...]`。
- 严格遵循参数类型与枚举值，不要传入额外字段或 `null`。

## 如何自测
- 执行 `python3 litmus.py check` 校验 `answer.json` 的 JSON 结构是否合法（不判对错）。
