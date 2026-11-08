# 修复阶梯档位查找

抄表计费按用量落在哪一档来取单价。档位边界保存在一个非递减的 `long` 数组里，当前的查找把「最后一个不大于目标的位置」写成了「第一个大于等于目标的位置」，重复边界和落在两档之间时会选错档。

## `metering.TierIndex`

`public static int floorIndex(long[] values, long target)`

- `values` 为 `null` 时抛出 `NullPointerException`。
- 调用方保证 `values` 非递减，里面可以有重复值。不要求你检查数组是否有序。
- 返回最后一个小于或等于 `target` 的下标。
- 数组为空，或者所有元素都大于 `target` 时，返回 `-1`。

例子：

- `{1, 2, 2, 2, 3}` 查找 `2`，返回 `3`
- `{1, 3, 5}` 查找 `4`，返回 `1`
- `{1, 3, 5}` 查找 `0`，返回 `-1`
- `{1, 3, 5}` 查找 `9`，返回 `2`
- `{4, 4, 4}` 查找 `4`，返回 `2`
- 空数组查找任意值，返回 `-1`

## 计费

`TariffPlan` 的构造参数是严格递增的档位起点 `thresholds`，以及等长的单价数组 `unitPriceFen`（单位：分 / 每个用量单位）。

- 任一数组为 `null` 时抛出 `NullPointerException`。
- 长度为 0、两边长度不同、或档位不是严格递增时，抛出 `IllegalArgumentException`。
- `unitPrice(long usage)` 用 `floorIndex` 选择单价。结果下标为 `-1` 时抛出 `IllegalArgumentException`，消息里包含 `用量`。
- 用量落在两档起点之间时取较低那一档。例如起点 `0, 100, 200`、单价 `10, 8, 5`，用量 `50` 的单价是 `10`，用量 `150` 的单价是 `8`，用量 `250` 的单价是 `5`。

`BillDraft.quote(TariffPlan plan, long usage)` 返回一张草稿，字段为：

- `usage`：传入的用量
- `unitPriceFen`：选中的单价
- `amountFen`：`usage * unitPriceFen`，用 `Math.multiplyExact` 计算，溢出抛出 `ArithmeticException`

`plan` 为 `null` 时抛出 `NullPointerException`。

只修改 `metering/` 下的 Java 源文件，不要改测试。代码只需使用 JDK 17 已有的 API。

## 如何自测

`python3 litmus.py check`
