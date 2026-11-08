# 修复访客缓存的淘汰顺序

门禁缓存容量有限。淘汰时应该先丢掉访问次数最少的记录；次数相同，再丢掉最久没有被访问的那条。当前实现把这两个条件的顺序弄反了，次数已经很高、只是更早被访问过的记录会先被清掉。

## `admission.VisitCache`

`public VisitCache(int capacity)`

- `capacity < 1` 时抛出 `IllegalArgumentException`。

`public String get(String key)`

- `key` 为 `null` 时抛出 `NullPointerException`。
- 没有这个键时返回 `null`，不新增记录，也不改变任何计数。
- 命中时访问次数加 1，并把这次访问记为最新，然后返回当前值。

`public void put(String key, String value)`

- `key` 或 `value` 为 `null` 时抛出 `NullPointerException`。
- 键已存在：替换值，访问次数加 1，这次访问记为最新，不淘汰其他记录。
- 键不存在且未满：插入，访问次数为 1，这次访问记为最新。
- 键不存在且已满：先淘汰一条，再插入新记录，新记录的访问次数为 1。

淘汰规则：

1. 访问次数更少的先淘汰。
2. 次数相同，则上次访问更早的先淘汰。
3. 每次成功的 `get` 和 `put` 都会产生一个新的访问序号，序号只增不减，不使用墙上时钟。

例子：容量为 2。

- `put("A", "a")`，再 `put("A", "a2")`，A 的次数是 2。
- `put("B", "b")`，B 的次数是 1，而且比 A 更新。
- `put("C", "c")` 时应淘汰 B。缓存里剩下 A 和 C，A 的值仍是 `a2`。

如果三次都是不同的新键，次数都是 1，则淘汰最早写入的那个。

`size()` 返回当前条目数。`accessCount(String key)` 返回次数，不存在时返回 `0`，并且不改变缓存。

只修改 `admission/` 下的 Java 源文件，不要改测试。

## 如何自测

`python3 litmus.py check`
