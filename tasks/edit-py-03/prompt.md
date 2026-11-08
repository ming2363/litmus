# edit-py-03: 扩展物流单号正则并修复文本提取边界

## 背景与需求

当前仓库是跨境仓储物流面单解析与校验工具（`src/identifiers.py`、`src/manifest.py`）。系统正在升级运单编号规则，`src/identifiers.py` 目前仅支持旧版固定格式 `站点(2字母)-20XX年份-5位流水号`（例如 `SH-2026-00412`），请仅在 `src/identifiers.py` 内修改匹配与解析逻辑，以支持新版运单编号规范：

### 新版运单编号格式规范

完整格式：`{site}[ -{zone} ]-{year}-{seq}[ -{suffix} ]`（各段以 `-` 连接，无空格）：

1. **站点码 `site`**：`2` 至 `3` 位 ASCII 大写字母（`A`–`Z`），例如 `SH`、`SZX`、`HKG`。
2. **可选分区码 `zone`**：紧跟站点后的 `-[A-Z][0-9]{2}`（`-` 加 1 位 ASCII 大写字母与 2 位 ASCII 数字，如 `-A01`、`-Z99`）。
3. **年份 `year`**：`-20[0-9]{2}`（4 位 ASCII 数字，固定以 `20` 开头，如 `2025`、`2026`）。
4. **流水号 `seq`**：`5` 至 `7` 位 ASCII 数字（`[0-9]{5,7}`）。
5. **可选退换标后缀 `suffix`**：末尾可选 `-[RX][0-9]`（`-` 加大写 `R` 或 `X` 与 1 位 ASCII 数字，如 `-R1`、`-X0`）。

### 函数行为与边界要求

需保持 `src/identifiers.py` 对外暴露的函数与语义（`src/manifest.py` 依赖它们）：

- `is_valid_parcel_code(code: str) -> bool`：
  - 仅当整个字符串严格匹配上述新版格式时返回 `True`，否则返回 `False`（含末尾换行符如 `"SH-2026-00412\n"`、非 str 输入或空串均返回 `False`）。
  - 大小写敏感，且数字与字母仅限 ASCII 字符。
- `parse_parcel_code(code: str) -> Optional[Dict[str, Optional[str]]]`：
  - 若 `code` 合法，返回字典：`{"site": ..., "zone": ..., "year": ..., "seq": ..., "suffix": ...}`，其中 `zone` 和 `suffix` 为不含前导 `-` 的值（未提供时为 `None`）；若 `code` 非法，返回 `None`。
- `extract_parcel_codes(text: str) -> List[str]`：
  - 按出现顺序从任意日志或清单文本中提取所有独立的合法运单编号字符串列表。
  - **独立编号边界**：候选编号左右两侧均不得紧邻 ASCII 字母、数字、下划线或连字符（即不能是 `[A-Za-z0-9_-]`），防止把诸如 `REF-SH-2026-00412`、`SH-2026-00412-R12`、`SH-2026-00412-Y1`、`ABCD-2026-00412`、`SH-2026-00412999` 误截断提取为合法编号。标点、空格、括号、换行及中文字符（如 `[SZX-A01-2026-123456-R2]`、`单号：SH-2026-00412。`）属于合法分隔符。

## 约束条件

- 只允许修改 `src/identifiers.py`。
- **改动行数上限 (`max_changed_lines`)：`25` 行**。
- 不得修改 `src/manifest.py` 或可见测试文件 `tests/test_public.py`。
- 仅使用 Python 标准库（兼容 Python 3.9～3.14），UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
