# feat-java-01: 订单校验器新增冷链配送规则

## 背景与需求

当前仓库是电商履约订单校验模块（包名 `com.litmus.order`），包含以下文件：
- `src/com/litmus/order/OrderItem.java`：订单明细项，含 `isColdChain()` 标识是否需要冷链配送。
- `src/com/litmus/order/Order.java`：订单实体，含配送方式 `shippingMethod` 与目标区域 `regionCode`。
- `src/com/litmus/order/ValidationResult.java`：校验结果（`isValid()`、`getErrorCodes()`、`getMessages()`）。
- `src/com/litmus/order/ShippingPolicy.java`：配送方式与区域策略配置。
- `src/com/litmus/order/OrderValidator.java`：订单校验器主逻辑。

目前系统尚未校验冷链商品的配送方式和覆盖区域。请修改 `ShippingPolicy.java` 与 `OrderValidator.java` 两个文件，新增冷链校验规则：

1. **完善配送策略 (`src/com/litmus/order/ShippingPolicy.java`)**：
   - `public static boolean supportsColdChainMethod(String shippingMethod)`：
     - 仅当 `shippingMethod` 为 `"COLD_EXPRESS"` 或 `"SAME_DAY"` 时返回 `true`，其余（包括 `"STANDARD"`、`"ECONOMY"`、`null` 或未知值）返回 `false`。
   - `public static boolean supportsColdChainRegion(String regionCode)`：
     - 仅当 `regionCode` 为 `"NORTH"`、`"EAST"` 或 `"SOUTH"` 时返回 `true`，其余（包括 `"WEST"`、`"REMOTE"`、`null` 等）返回 `false`。

2. **接入订单校验 (`src/com/litmus/order/OrderValidator.java`)**：
   - 当且仅当订单中至少包含一件 `item.isColdChain() == true` 的商品时，执行以下两条冷链校验：
     - 若 `!ShippingPolicy.supportsColdChainMethod(order.getShippingMethod())`，向错误列表追加错误码 `"COLD_CHAIN_METHOD_UNSUPPORTED"`（附非空错误描述）。
     - 若 `!ShippingPolicy.supportsColdChainRegion(order.getRegionCode())`，向错误列表追加错误码 `"COLD_CHAIN_REGION_UNSUPPORTED"`（附非空错误描述）。
   - 注意：若两条规则同时不满足，两个错误码均需加入 `ValidationResult.getErrorCodes()`；若订单中没有任何冷链商品，原有配送方式与区域校验规则保持不变（例如普通商品使用 `"STANDARD"` 发往 `"REMOTE"` 依然合法）。

## 约束条件

- 只允许修改 `src/**/*.java` 范围内的文件。
- 不得修改或删除可见测试文件 `src/com/litmus/order/OrderValidatorPublicTest.java`。
- 仅使用 JDK 17 标准库，不使用第三方依赖；全部文件 UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
