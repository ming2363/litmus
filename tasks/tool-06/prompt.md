# tool-06: 隐含前置条件补齐与发布调用

## 背景与需求
请阅读工作目录下的 `release_request.txt`、`cluster_state.json` 和 `deploy_policy.md`。
用户的直接诉求是完成一次版本发布，但执行发布前必须核查各项前置条件是否已经满足：**对于尚未满足的前提条件，必须先按规则顺序调用相应工具补齐；对于已经满足的前置条件，严禁重复调用**。请将最终所需的完整有序调用序列写入工作目录根下的 `answer.json`。

## 工具定义（JSON Schema）
```json
[
  {
    "name": "build_image",
    "description": "构建指定服务与版本的容器镜像",
    "parameters": {
      "type": "object",
      "properties": {
        "service": {
          "type": "string"
        },
        "version": {
          "type": "string"
        }
      },
      "required": [
        "service",
        "version"
      ]
    }
  },
  {
    "name": "run_smoke_tests",
    "description": "运行服务冒烟测试套件",
    "parameters": {
      "type": "object",
      "properties": {
        "service": {
          "type": "string"
        },
        "version": {
          "type": "string"
        }
      },
      "required": [
        "service",
        "version"
      ]
    }
  },
  {
    "name": "sync_cluster_config",
    "description": "同步目标集群的基础配置映射",
    "parameters": {
      "type": "object",
      "properties": {
        "cluster": {
          "type": "string"
        }
      },
      "required": [
        "cluster"
      ]
    }
  },
  {
    "name": "sign_artifact",
    "description": "对构建产物执行发布签名校验",
    "parameters": {
      "type": "object",
      "properties": {
        "service": {
          "type": "string"
        },
        "version": {
          "type": "string"
        }
      },
      "required": [
        "service",
        "version"
      ]
    }
  },
  {
    "name": "acquire_deploy_lock",
    "description": "为操作人申请目标生产集群的发布互斥锁",
    "parameters": {
      "type": "object",
      "properties": {
        "cluster": {
          "type": "string"
        },
        "owner": {
          "type": "string"
        }
      },
      "required": [
        "cluster",
        "owner"
      ]
    }
  },
  {
    "name": "deploy_release",
    "description": "正式把已签名的服务版本发布到已加锁的目标集群",
    "parameters": {
      "type": "object",
      "properties": {
        "service": {
          "type": "string"
        },
        "version": {
          "type": "string"
        },
        "cluster": {
          "type": "string"
        }
      },
      "required": [
        "service",
        "version",
        "cluster"
      ]
    }
  }
]
```

## 答案格式与约束
- `answer.json` 必须为有序 JSON 数组：`[{"name": ..., "args": {...}}, ...]`。
- 严格遵循参数名称与类型，不要传入额外字段或 `null`。

## 如何自测
- 执行 `python3 litmus.py check` 校验 `answer.json` 的 JSON 结构是否合法（不判对错）。
