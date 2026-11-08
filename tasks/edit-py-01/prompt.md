# edit-py-01: 修改客户端默认超时并增加参数范围校验

## 背景与需求

当前仓库是一个基于可注入传输层的轻量 HTTP 重试客户端（`src/client.py`、`src/models.py`）。

请仅对 `src/client.py` 做小范围精确修改，满足以下要求：

1. **修改默认超时时间**：
   - 将 `DEFAULT_TIMEOUT` 及 `HttpClient.__init__` 的默认 `timeout` 参数从 `30.0` 修改为 `5.0`（秒）。
2. **增加参数范围校验**：
   - **构造与请求时的 `timeout`**：必须是有限数值（`int` 或 `float`，且不能为 `bool`、`NaN`、`inf`），且满足闭区间 `0.1 <= timeout <= 60.0`；不满足时抛出 `ValueError`。（包括 `__init__(..., timeout=...)` 与 `request(..., timeout=...)` 传入非 `None` 覆盖值时均需校验。）
   - **构造时的 `max_retries`**：必须是整数（`int`，不能为 `bool` 或 `float`），且满足闭区间 `0 <= max_retries <= 5`；不满足时抛出 `ValueError`。
3. 保持所有已有成功响应解析、重试逻辑与异常行为不变。

## 约束条件

- 只允许修改 `src/client.py`。
- **改动行数上限 (`max_changed_lines`)：`20` 行**（按统一换行符并去除行尾空白后的 diff 统计）。
- 不得修改或删除可见测试文件 `tests/test_public.py`。
- 仅使用 Python 标准库（兼容 Python 3.9～3.14），UTF-8 编码，LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
