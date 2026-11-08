# 修复门店销售报表

夜班对账用 sqlite3 汇总各门店订单。现在没有成交的门店会从报表里消失，金额为空的已支付订单也不计入笔数，退款笔数也被滤掉了。请按下面的口径改正查询。

## 表

`ledger.schema.init_db(conn)` 在已打开的连接上建表：

- `stores(id INTEGER PRIMARY KEY, name TEXT NOT NULL, region TEXT NOT NULL)`
- `orders(id INTEGER PRIMARY KEY, store_id INTEGER NOT NULL, status TEXT NOT NULL, amount_cents INTEGER, ordered_on TEXT NOT NULL)`

`amount_cents` 允许为 `NULL`。`status` 只用到 `paid`、`refunded`、`pending` 三种文本。测试会自己插入数据，不会依赖预置行。

## `store_paid_report(conn)`

返回每个门店一行的 `list[dict]`，按 `store_id` 升序。即使该门店没有任何订单，也必须有一行。每个字典的键为：

- `store_id`：整数
- `store_name`：门店名
- `region`：区域
- `paid_orders`：`status` 为 `paid` 的订单数。`amount_cents` 为 `NULL` 的已支付订单也要计入
- `paid_amount_cents`：这些已支付订单的 `amount_cents` 之和。`NULL` 金额按 0。没有任何已支付订单时是 `0`，不能是 `None`
- `refunded_orders`：`status` 为 `refunded` 的订单数。没有时是 `0`

`pending` 不计入笔数，也不计入金额。三个数字字段都必须是 `int`。

## `daily_paid_total(conn, day)`

返回 `ordered_on` 等于 `day` 且 `status` 为 `paid` 的金额合计，`NULL` 金额按 0，没有订单时返回 `0`。这个函数的现有口径是对的，修改报表时不要把它改坏。

只修改 `ledger/` 下的 Python 文件，不要改测试。查询必须给出确定结果，不要依赖未指定的排序之外的行顺序。

## 如何自测

`python3 litmus.py check`
