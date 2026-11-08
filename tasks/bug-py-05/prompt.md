# 修复包房时段合并过慢

预约系统要把一批半开区间合并成不重叠的占用时段。小数据的结果是对的，但几千段以上会慢到无法在一次排班里算完。请保持结果不变，并让大规模输入在 1 秒内完成。

## 区间

每个区间是 `(start, end)`，表示半开区间 `[start, end)`。`start` 和 `end` 必须是 `int`，且不能是 `bool`，还要满足 `start < end`。否则 `merge_intervals` 抛出 `ValueError`。

两个区间只要边界相接（前一个 `end` 等于后一个 `start`）或有重叠，就合并成一个。合并结果按 `start` 升序，区间之间不再相接或重叠。函数返回新的 `list[tuple]`，不修改入参的内部结构。

负数端点允许。空列表返回空列表。

`BookingCalendar.add(start, end)` 记录一段预约。`ranges()` 返回当前全部预约合并后的区间，规则与 `merge_intervals` 相同。`BookingCalendar.from_pairs(pairs)` 用一批区间构造日历。

八万段互不相交的区间，以及八万段首尾重叠、最终合成一段的区间，都要在 1 秒内得到正确结果。

只修改 `booking/` 下的 Python 文件，不要改测试。

## 如何自测

`python3 litmus.py check`
