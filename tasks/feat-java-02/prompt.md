# feat-java-02: 重构支付渠道 switch 为策略接口并新增渠道

## 背景与需求

当前仓库是一个清结算网关支付处理模块（包名 `com.litmus.pay`），目前通过散落在多个类中的 `switch (channel)` 处理不同支付渠道的逻辑：
- `PaymentChannel.java`：支付渠道枚举（当前含 `CARD`、`BANK_TRANSFER`、`E_WALLET`）与 `fromCode(String)`。
- `PaymentRequest.java` / `PaymentReceipt.java`：支付请求与回执模型。
- `RiskChecker.java`：按渠道做币种与单笔金额风控校验（内部使用 `switch`）。
- `FeeCalculator.java`：按渠道计算手续费（内部使用 `switch`）。
- `PaymentGateway.java`：交易处理入口，协调校验、算费与生成参考号（内部使用 `switch`）。

随着渠道增多，多处重复 `switch` 难以维护。请你完成以下重构与新渠道扩展（涉及跨 5 个以上文件的协调改动）：

### 1. 抽取策略接口并消除 `switch`

- 新增接口 `src/com/litmus/pay/PaymentChannelStrategy.java`（包名 `com.litmus.pay`），精确定义以下方法：
  - `PaymentChannel channel();`
  - `void validate(PaymentRequest request);`
  - `long calculateFee(long amountCents, String currency);`
  - `String buildReference(PaymentRequest request);`
- 为每个渠道提供策略实现（可放在独立类文件或策略包内），并将 `RiskChecker`、`FeeCalculator`、`PaymentGateway` 重构为通过策略映射表（`Map<PaymentChannel, PaymentChannelStrategy>`）委托执行，彻底消除这 3 个类中的渠道 `switch` 分支。
- 保持 `RiskChecker`、`FeeCalculator`、`PaymentGateway` 原有无参构造器与公开方法签名兼容（默认加载全部内置渠道策略），同时为这 3 个类各自新增支持注入自定义策略集合的构造器：
  - `public RiskChecker(Collection<PaymentChannelStrategy> strategies)`
  - `public FeeCalculator(Collection<PaymentChannelStrategy> strategies)`
  - `public PaymentGateway(Collection<PaymentChannelStrategy> strategies)`
  （当遇到未注册的渠道或 `null` 策略时，抛出 `IllegalArgumentException`。）

### 2. 保持已有渠道行为完全不变

- `CARD`、`BANK_TRANSFER`、`E_WALLET` 的币种限制、单笔金额上下限、手续费计算公式、参考号格式及非法输入抛 `IllegalArgumentException` 的语义必须与现有实现完全一致。

### 3. 新增支付渠道 `DIRECT_DEBIT`

- 在 `PaymentChannel` 枚举中新增 `DIRECT_DEBIT`（`PaymentChannel.fromCode("DIRECT_DEBIT")` 可正常解析）。
- 业务规则如下：
  - **支持币种**：仅 `"USD"` 与 `"EUR"`（其他币种或 `null` 抛 `IllegalArgumentException`）。
  - **单笔金额范围**：`[100, 500_000]` 分（闭区间，超出范围抛 `IllegalArgumentException`）。
  - **手续费公式**：`Math.min(1500L, Math.max(100L, 50L + (amountCents * 5L) / 1000L))`（含基础校验：不支持币种或 `amountCents <= 0` 抛 `IllegalArgumentException`）。
  - **参考号格式**：`"DD-" + request.getOrderId() + "-" + request.getCurrency()`。

## 约束条件

- 只允许修改或新增 `src/**/*.java` 范围内的文件。
- 不得修改或删除可见测试文件 `src/com/litmus/pay/PaymentGatewayPublicTest.java`。
- 仅使用 JDK 17 标准库；全部文件 UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
