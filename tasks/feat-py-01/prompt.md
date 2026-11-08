# feat-py-01: 记账命令行工具新增 --since 日期过滤

## 背景与需求

当前仓库是一个个人收支记账命令行工具，账目以 CSV 格式存储（表头为 `id,date,category,kind,amount_cents,note`），已支持 `list`（列出明细）和 `summary`（按分类汇总收支与净结余）两个子命令，并支持按 `--category` 过滤。

请为该工具新增按起始日期过滤的 `--since` 功能，具体要求如下：

1. **严格日期解析 (`src/models.py`)**：
   - 完善 `parse_iso_date(text: str) -> datetime.date`：
   - 仅接受严格 `YYYY-MM-DD` 格式的合法公历日期（例如 `"2026-03-10"`）。
   - 对于格式不符（如 `"20260310"`、`"2026/03/10"`、`""`、前后含空白或非字符串）或非法日历日期（如 `"2026-02-30"`），必须抛出 `ValueError`。

2. **过滤逻辑 (`src/ledger.py`)**：
   - 将 `filter_entries` 的签名扩展为：
     `filter_entries(entries: Sequence[LedgerEntry], *, category: Optional[str] = None, since: Optional[date] = None) -> List[LedgerEntry]`
   - 当 `since` 不为 `None` 时，仅保留交易日期满足 `entry.tx_date >= since`（包含 `since` 当天）的记录，并保持原有顺序。
   - `category` 与 `since` 同时传入时，需同时满足两个条件（逻辑与）。

3. **命令行参数 (`src/cli.py`)**：
   - 为 `list` 和 `summary` 两个子命令均新增可选参数 `--since`（格式 `YYYY-MM-DD`）。
   - 传入 `--since` 时，先校验日期格式并过滤记录，再执行列出明细或分类汇总；即使过滤后没有记录，也应正常输出空明细或全 0 汇总（退出码 `0`）。
   - 当 `--since` 参数不是合法的 `YYYY-MM-DD` 日期时，向错误输出打印提示信息，并以非零状态退出（`main(argv)` 返回非 `0` 整数退出码或抛出非 `0` 码的 `SystemExit`）。
   - 保持不传 `--since` 时所有原有行为和输出格式不变。

## 约束条件

- 只允许修改 `src/*.py` 范围内的文件。
- 不得修改或删除可见测试文件 `tests/test_public.py`。
- 仅使用 Python 标准库（兼容 Python 3.9～3.14），UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
