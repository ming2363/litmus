# term-02: CSV 订单分组统计汇总

## 背景与需求
工作目录下的 `data/orders.csv` 记录了各区域的订单明细（标准 UTF-8 CSV，含表头 `order_id,region,category,amount,status`，部分 `category` 字段包含逗号并使用双引号包裹）。
请统计已完成订单的分区域汇总结果，并写入工作目录根下的 `region_stats.json`。

## 统计与输出格式要求
1. 仅统计 `status` 严格等于 `completed` 的订单行（忽略 `cancelled`、`refunded`、`pending`）。
2. 按 `region` 分组，结果按 `region` 字典序升序排列。
3. `region_stats.json` 必须是一个 JSON 数组，每个元素为对象，包含且仅包含以下 4 个字段：
   - `region`（字符串）：区域名称
   - `order_count`（整数）：该区域已完成订单数
   - `total_amount`（数值）：该区域已完成订单总金额（保留 2 位小数）
   - `avg_amount`（数值）：该区域已完成订单平均金额（`total_amount / order_count`，保留 2 位小数）

## 如何自测
- 可在工作目录核对生成的 `region_stats.json` 结构与数值，也可执行 `python3 litmus.py check` 检查工作目录无违规符号链接。
