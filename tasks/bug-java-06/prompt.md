# 修复渠道手续费少一分

对账时，渠道手续费按「金额（分）× 费率」计算，结果要回到整数分。当前舍入把刚好处于半分的结果少算了一分，一批订单累加后和对账单对不上。

## 规则

`settlement.ChannelFee.feeFen(long amountFen, BigDecimal rate)`

- `rate` 为 `null` 时抛出 `NullPointerException`。
- `amountFen` 小于 0，或 `rate` 小于 0 时，抛出 `IllegalArgumentException`，消息里包含 `不能为负`。费率 `0` 合法。
- 手续费（分）= 把 `amountFen * rate` 这一次乘法的精确结果，按四舍五入到整数分。
- 半分必须远离 0 的方向进位，也就是 `RoundingMode.HALF_UP`，不是直接舍去，也不是银行家舍入（`HALF_EVEN`）。
- 只舍入一次。不要先把金额换成元、乘完费率再换回分。
- 结果用 `long` 返回。`10000` 分乘费率 `0.006` 得到 `60`。`250` 分乘 `0.006` 得到 `1.5`，应进成 `2`。`5` 分乘 `0.5` 得到 `2.5`，应进成 `3`。`1` 分乘 `0.5` 得到 `0.5`，应进成 `1`。

`settlement.Statement.totalFee(long[] amounts, BigDecimal rate)` 把每笔金额的手续费相加。`amounts` 为 `null` 时抛出 `NullPointerException`。空数组返回 `0`。

`settlement.Reconciliation.differenceFen(long[] amounts, BigDecimal rate, long settledFeeFen)` 返回我方手续费合计减去渠道已结手续费。差值为 `0` 表示对齐。

费率使用 `BigDecimal` 的十进制值，例如 `new BigDecimal("0.006")`，不要经过 `double`。

只修改 `settlement/` 下的 Java 源文件，不要改测试。

## 如何自测

`python3 litmus.py check`
