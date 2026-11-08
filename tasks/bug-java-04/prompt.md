# 修复入住天数在夏令时差一天

酒店按客人入住地的本地日历计算晚数。现在的实现用两个时刻之间的物理时长除以 24 小时，跨过夏令时或者不足 24 小时但跨过本地午夜时，就会少算或多算一天。

## `stay.LocalSpan`

`public static long calendarDaysBetween(Instant start, Instant end, ZoneId zone)`

- 任一参数为 `null` 时抛出 `NullPointerException`。
- 把 `start` 和 `end` 分别换算成 `zone` 的本地日期，返回结束日期减去开始日期的天数。
- 这是日历差，不是 `Duration.toDays()`。不满 24 小时但本地日期已经不同，结果是 `1` 或 `-1`。本地日期相同，即使物理时间达到 24 小时，结果也是 `0`。
- `end` 的本地日期更早时，结果为负数。

例子：

- `Asia/Shanghai`：`2026-05-01T02:00:00Z` 到 `2026-05-02T01:00:00Z` 只有 23 小时，本地日期从 5 月 1 日到 5 月 2 日，结果是 `1`。
- `America/New_York`：`2026-03-08T05:30:00Z` 到 `2026-03-09T04:30:00Z` 跨过春令时，实际 23 小时，日历差是 `1`。
- `America/New_York`：`2026-11-01T04:30:00Z` 到 `2026-11-02T04:30:00Z` 跨过秋令时，实际 24 小时，但两个时刻的本地日期都是 `2026-11-01`，结果是 `0`。

必须使用传入的 `ZoneId`，不能写死某一个时区。

## 报价

`StayQuote.nights(Instant checkIn, Instant checkOut, ZoneId zone)` 与 `calendarDaysBetween` 相同。

`StayQuote.totalFen(Instant checkIn, Instant checkOut, ZoneId zone, long nightlyFen)` 返回晚数乘以每晚房价（分）。晚数小于 0 时抛出 `IllegalArgumentException`，消息里包含 `退房`。`nightlyFen` 小于 0 时同样抛出 `IllegalArgumentException`。乘法使用 `Math.multiplyExact`。

只修改 `stay/` 下的 Java 源文件，不要改测试。

## 如何自测

`python3 litmus.py check`
