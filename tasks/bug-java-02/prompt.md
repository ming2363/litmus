# 修复命中计数在并发下丢失

接口统计用 `HitCounter` 按键累加次数。多个线程同时对同一个键 `increment` 时，最终计数会小于实际调用次数。请让并发更新不再丢失。

## `hitcount.HitCounter`

- `increment(String key, long delta)`：把 `delta` 加到 `key` 上。`key` 为 `null` 时抛出 `NullPointerException`。`delta` 可以是任意 `long`，包括负数和 0。键不存在时从 0 开始加。
- `get(String key)`：返回当前计数。键不存在时返回 `0`。`key` 为 `null` 时抛出 `NullPointerException`。
- `snapshot()`：返回一份新的映射，键按字典序排列。之后再调用 `increment`，或者修改返回的映射，都不影响另一方。

键按原样比较，区分大小写，不裁剪空白。

多个线程可以同时 `increment` 和 `get`。所有 `increment` 都结束后，再调用 `get`，结果必须等于这些 `delta` 的代数和。不同键互不影响。

`hitcount.HitReport.render(HitCounter counter)` 按 `snapshot` 的顺序输出 `键=计数`，每行一条，以换行结尾。没有键时返回空字符串。

只修改 `hitcount/` 下的 Java 源文件，不要改测试。不要依赖睡眠时间来碰运气，结果必须稳定。

## 如何自测

`python3 litmus.py check`
