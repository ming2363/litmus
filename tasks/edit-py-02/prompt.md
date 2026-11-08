# edit-py-02: 为关税运费计算函数增加可选缓存并保持签名兼容

## 背景与需求

当前仓库是一个跨境运费与税费报价计算模块（`src/pricing.py`、`src/rules.py`）。核心入口为 `src/pricing.py` 中的 `compute_tariff`：

```python
def compute_tariff(
    origin: str,
    dest: str,
    weight_grams: int,
    tier: str = "standard",
    overrides: Optional[Dict[str, float]] = None,
    *,
    rate_provider: Optional[Callable[[str, str, str], int]] = None,
) -> Dict[str, Any]:
```

当外部调用方在批量试算中高频重复查询相同线路、重量与费率参数时，底层 `rate_provider` 会被反复触发。请仅在 `src/pricing.py` 内进行小范围修改，为 `compute_tariff` 新增可选缓存能力，并严格满足以下兼容性与边界要求：

1. **签名兼容与默认行为**：
   - 在 `compute_tariff` 参数列表末尾新增关键字参数 `use_cache: bool = False`（不得改变已有 5 个位置/关键字参数与 `rate_provider` 的顺序、名称和默认值）。
   - 同时新增模块级函数 `clear_tariff_cache() -> None` 用于清空缓存。
   - 当 `use_cache=False`（默认）时，行为必须与原实现完全一致（每次均实时计算并调用 `rate_provider`，不读取也不写入缓存）。
2. **缓存键归一化与不可哈希参数处理**：
   - `overrides` 是普通字典（不可直接哈希），不能因为传入 `overrides={"express": 0.9}` 而抛出 `TypeError`。
   - `overrides` 为 `None` 与 `{}` 视为等价；字典内键值对顺序不同但内容相同时应共享同一缓存条目；不同 `overrides` 内容必须严格区分。
   - 以位置参数或关键字参数传入等价实参时（例如显式传 `tier="standard"` 与省略默认值），应命中同一缓存条目。
   - 不同的 `rate_provider` 函数（以及默认的 `rate_provider=None`）之间缓存必须相互隔离，不能把 A 费率源的缓存结果返回给 B 费率源。
3. **返回值可变性隔离**：
   - `compute_tariff` 返回的字典及其内部的列表（如 `"tags"`）是可变对象。即使调用方修改了某次返回值中的字段或列表元素，也不得污染后续缓存命中的返回结果。
4. **异常不入缓存**：
   - 非法参数或 `rate_provider` 抛出的异常应原样抛出，不得存入缓存。

## 约束条件

- 只允许修改 `src/pricing.py`。
- **改动行数上限 (`max_changed_lines`)：`35` 行**。
- 不得修改或删除可见测试文件 `tests/test_public.py`。
- 仅使用 Python 标准库（兼容 Python 3.9～3.14），UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
