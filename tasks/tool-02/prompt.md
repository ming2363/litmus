# tool-02: 判断工具能力边界

## 背景与需求
请阅读工作目录下的 `request.txt`，判断下方可用工具中是否存在能够满足该需求的调用。
如果不存在任何合适工具能够执行用户请求的操作，**请勿强行调用只读查询或无关工具**，应在 `answer.json` 中写入空列表 `[]`。

## 工具定义（JSON Schema）
```json
[
  {
    "name": "describe_deployment",
    "description": "只读查询指定命名空间下 Deployment 的当前副本数、镜像版本与环境变量摘要",
    "parameters": {
      "type": "object",
      "properties": {
        "namespace": {
          "type": "string"
        },
        "deployment": {
          "type": "string"
        }
      },
      "required": [
        "namespace",
        "deployment"
      ]
    }
  },
  {
    "name": "get_service_health",
    "description": "只读查询微服务的健康检查状态",
    "parameters": {
      "type": "object",
      "properties": {
        "service": {
          "type": "string"
        },
        "environment": {
          "type": "string"
        }
      },
      "required": [
        "service",
        "environment"
      ]
    }
  },
  {
    "name": "query_cpu_metrics",
    "description": "只读查询工作负载的 CPU 利用率曲线",
    "parameters": {
      "type": "object",
      "properties": {
        "namespace": {
          "type": "string"
        },
        "deployment": {
          "type": "string"
        },
        "window_minutes": {
          "type": "integer"
        }
      },
      "required": [
        "namespace",
        "deployment",
        "window_minutes"
      ]
    }
  },
  {
    "name": "list_active_alerts",
    "description": "只读列出当前触发中的告警",
    "parameters": {
      "type": "object",
      "properties": {
        "severity": {
          "type": "string",
          "enum": [
            "info",
            "warning",
            "critical"
          ]
        }
      },
      "required": [
        "severity"
      ]
    }
  },
  {
    "name": "fetch_pod_logs",
    "description": "只读拉取 Pod 最近若干行标准输出日志",
    "parameters": {
      "type": "object",
      "properties": {
        "namespace": {
          "type": "string"
        },
        "pod_prefix": {
          "type": "string"
        },
        "tail_lines": {
          "type": "integer"
        }
      },
      "required": [
        "namespace",
        "pod_prefix",
        "tail_lines"
      ]
    }
  }
]
```

## 答案格式与约束
- `answer.json` 必须为 JSON 数组：`[{"name": ..., "args": {...}}]`，无合适工具时写入 `[]`。

## 如何自测
- 执行 `python3 litmus.py check` 校验 `answer.json` 的 JSON 结构是否合法（不判对错）。
