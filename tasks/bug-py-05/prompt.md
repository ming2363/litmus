# 修复巷道占用归并

北港调度把同一巷道上两段占用交给账本。两段之间没有空出来的分钟，结果却仍是两段。

复现：

```python
holds = [(0, 10, "A"), (10, 20, "A")]
blocks = []
WharfLedger().plan(holds, blocks)
```

期望得到 `[(0, 20, "A")]`。现在得到的是两段分开的占用。

`WharfLedger.plan(holds, blocks)` 接收两组序列。`holds` 的元素是 `(start, end, lane)`，`blocks` 的元素是 `(start, end)`。合法输入返回新的 `list`，元素是 `(start, end, lane)`。非法输入抛出 `ValueError`。

账本的现行口径写在 `docs/调度台说明.md`。修好之后，`plan` 要在所有输入上符合这份口径，验收不只看上面这个例子。

只修改 `wharfbook/` 下的 Python 文件，不要改测试。

## 如何自测

`python3 litmus.py check`
