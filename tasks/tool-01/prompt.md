# tool-01: 对象存储桶生命周期规则配置

## 背景与需求
请阅读工作目录下的 `request.txt`，根据需求从下方工具定义中选择唯一合适的工具并提取参数，将工具调用列表写入工作目录根下的 `answer.json`。

## 工具定义（JSON Schema）
```json
[
  {
    "name": "get_bucket_info",
    "description": "查询指定对象存储桶的当前配置与容量信息",
    "parameters": {
      "type": "object",
      "properties": {
        "bucket": {
          "type": "string"
        }
      },
      "required": [
        "bucket"
      ]
    }
  },
  {
    "name": "list_buckets",
    "description": "列出某区域下的对象存储桶清单",
    "parameters": {
      "type": "object",
      "properties": {
        "region": {
          "type": "string"
        }
      },
      "required": [
        "region"
      ]
    }
  },
  {
    "name": "set_bucket_lifecycle",
    "description": "为存储桶配置对象归档与过期删除生命周期规则",
    "parameters": {
      "type": "object",
      "properties": {
        "bucket": {
          "type": "string",
          "description": "存储桶名称"
        },
        "archive_after_days": {
          "type": "integer",
          "description": "多少天后转储"
        },
        "storage_tier": {
          "type": "string",
          "enum": [
            "standard_ia",
            "cold",
            "glacier"
          ],
          "description": "归档目标存储层"
        },
        "expire_after_days": {
          "type": "integer",
          "description": "多少天后彻底过期删除"
        },
        "dry_run": {
          "type": "boolean",
          "description": "是否仅预演而不立即生效"
        }
      },
      "required": [
        "bucket",
        "archive_after_days",
        "storage_tier",
        "expire_after_days",
        "dry_run"
      ]
    }
  },
  {
    "name": "delete_bucket",
    "description": "删除空存储桶",
    "parameters": {
      "type": "object",
      "properties": {
        "bucket": {
          "type": "string"
        },
        "force": {
          "type": "boolean"
        }
      },
      "required": [
        "bucket",
        "force"
      ]
    }
  }
]
```

## 答案格式与约束
1. `answer.json` 必须为 JSON 数组：`[{"name": "<工具名>", "args": {...}}]`。
2. 必须严格使用 schema 中定义的参数名与类型，不要传入未定义的额外参数或 `null`。

## 如何自测
- 执行 `python3 litmus.py check` 校验 `answer.json` 的 JSON 结构是否合法（不判对错）。
