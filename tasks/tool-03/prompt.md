# tool-03: 先校验用户再下单的顺序工具调用

## 背景与需求
请阅读工作目录下的 `order_request.md`、`directory.json` 和 `catalog.json`，生成符合企业采购风控流程的工具调用序列，写入工作目录根下的 `answer.json`。

## 采购合规流程（重要）
1. 下单风控规则规定：**提交采购订单前，必须先调用 `lookup_user` 对下单人的账户状态与可用额度进行实时校验，然后再调用 `create_order` 提交订单**。调用顺序严格不可颠倒，也不得跳过 `lookup_user`。
2. 由于本题在离线环境生成调用序列，调用 `create_order` 所需的准确 `user_id` 和商品 `sku` 请从工作目录的 `directory.json`（员工名录）与 `catalog.json`（物资目录）中核对确认，注意区分同名或停用账号及已下架型号。

## 工具定义（JSON Schema）
```json
[
  {
    "name": "lookup_user",
    "description": "按企业邮箱实时查询并校验采购员工的账户状态与用户 ID（下单前必调）",
    "parameters": {
      "type": "object",
      "properties": {
        "email": {
          "type": "string",
          "description": "员工企业邮箱"
        }
      },
      "required": [
        "email"
      ]
    }
  },
  {
    "name": "create_order",
    "description": "为已校验的员工提交内部物资采购订单",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {
          "type": "string",
          "description": "员工唯一用户 ID"
        },
        "sku": {
          "type": "string",
          "description": "商品 SKU 编号"
        },
        "quantity": {
          "type": "integer",
          "description": "采购数量"
        },
        "delivery_zone": {
          "type": "string",
          "description": "楼层配送区域标识"
        }
      },
      "required": [
        "user_id",
        "sku",
        "quantity",
        "delivery_zone"
      ]
    }
  },
  {
    "name": "list_orders",
    "description": "查询指定用户历史采购订单列表",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {
          "type": "string"
        }
      },
      "required": [
        "user_id"
      ]
    }
  },
  {
    "name": "cancel_order",
    "description": "取消尚未发货的采购订单",
    "parameters": {
      "type": "object",
      "properties": {
        "order_id": {
          "type": "string"
        },
        "reason": {
          "type": "string"
        }
      },
      "required": [
        "order_id",
        "reason"
      ]
    }
  },
  {
    "name": "update_shipping_address",
    "description": "修改已创建订单的配送区域",
    "parameters": {
      "type": "object",
      "properties": {
        "order_id": {
          "type": "string"
        },
        "delivery_zone": {
          "type": "string"
        }
      },
      "required": [
        "order_id",
        "delivery_zone"
      ]
    }
  }
]
```

## 答案格式与约束
- `answer.json` 必须为有序 JSON 数组：`[{"name": ..., "args": {...}}, ...]`。
- 仅传递各工具 schema 规定的必填参数，不要附加未定义参数或 `null`。

## 如何自测
- 执行 `python3 litmus.py check` 校验 `answer.json` 的 JSON 结构是否合法（不判对错）。
