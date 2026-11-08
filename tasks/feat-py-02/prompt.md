# feat-py-02: SQLite 按月汇总与环比报表

## 背景与需求

当前仓库是一个基于标准库 `sqlite3` 的 SaaS 订阅计费分析模块。数据库包含 4 张表（定义见 `src/db.py`）：

- `customers(id, name, region)`
- `plans(id, code, monthly_cents)`
- `invoices(id, customer_id, plan_id, billed_at, amount_cents, status)`（`billed_at` 为 `YYYY-MM-DD`，`status` 取值为 `'paid'` / `'void'` / `'pending'`）
- `refunds(id, invoice_id, refunded_at, amount_cents)`（`refunded_at` 为 `YYYY-MM-DD`，一笔发票可能对应 0 条、1 条或多条部分退款）

目前 `src/reports.py` 已提供按套餐汇总（`plan_revenue_summary`）和按客户净消费汇总（`customer_net_spend`），但 `monthly_revenue_report` 尚未实现。

请实现 `src/reports.py` 中的 `monthly_revenue_report` 函数：

```python
def monthly_revenue_report(
    conn: sqlite3.Connection,
    start_month: str,
    end_month: str,
    region: Optional[str] = None,
) -> List[Dict[str, Any]]:
```

### 详细业务规则

1. **月份参数校验**：
   - `start_month`、`end_month` 必须为严格 `YYYY-MM` 格式且月份在 `01`～`12` 之间，同时满足 `start_month <= end_month`；否则抛出 `ValueError`。
2. **连续自然月输出**：
   - 返回列表必须覆盖闭区间 `[start_month, end_month]` 内的**每一个自然月**（即使该月没有任何开票与退款，也必须输出全 0 行），按 `month` 升序排列。
3. **金额口径（单位均为整数分）**：
   - `month`：`str`，格式 `"YYYY-MM"`。
   - `gross_cents`：`int`，当月 `billed_at` 落在该月且 `invoices.status = 'paid'` 的发票 `amount_cents` 之和（无记录为 `0`）。
   - `refund_cents`：`int`，当月 `refunded_at` 落在该月且关联发票 `status = 'paid'` 的退款 `amount_cents` 之和（无记录为 `0`）。注意一笔发票可能有多条退款，切勿因连接产生重复计数。
   - `net_cents`：`int`，等于 `gross_cents - refund_cents`（当退款大于开票时可为负数）。
4. **环比指标（按报表区间内相邻自然月顺序计算）**：
   - `prev_net_cents`：`Optional[int]`，上一自然月的 `net_cents`；区间首月为 `None`。
   - `mom_diff_cents`：`Optional[int]`，等于 `net_cents - prev_net_cents`；区间首月为 `None`。
   - `mom_growth_pct`：`Optional[float]`，当 `prev_net_cents` 不为 `None` 且 `prev_net_cents > 0` 时，等于 `round((net_cents - prev_net_cents) * 100.0 / prev_net_cents, 2)`；当首月、`prev_net_cents == 0` 或 `prev_net_cents < 0` 时，均为 `None`。
5. **可选区域过滤**：
   - 当 `region` 不为 `None` 时，仅统计所属客户 `customers.region == region` 的发票与关联退款；区间内所有自然月仍须全部保留输出。

## 约束条件

- 只允许修改 `src/*.py` 范围内的文件。
- 不得修改或删除可见测试文件 `tests/test_public.py`。
- 仅使用 Python 标准库（`sqlite3` 等，兼容 Python 3.9～3.14），UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
