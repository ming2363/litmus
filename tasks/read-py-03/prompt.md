# read-py-03: 胸卡编码落库前的转换

## 背景

访客胸卡把原始字段 `badge_raw` 写成表 `guest_badge` 的列 `badge_code`。日志和展示用的是别的链路。

请列出写入列 `badge_code` 之前，值依次经过的转换函数。

## 判定规则

1. 只算 `badgedesk.store.writer.BadgeWriter#write_guest` 写进 `self.rows` 的那条链路。
2. 日志副本和 `badge_display` 预览链路不要算进去。
3. 顺序是运行时的调用顺序。基础步骤后面追加的函数也要按追加顺序列入。
4. 函数写成 `模块.函数名`，不要写类名。

## 答案

写入工作目录根的 `answer.json`：

```json
{"column": "badge_code", "pipeline": ["模块.函数名"]}
```

## 如何自测

执行 `python3 litmus.py check`。该命令只检查 JSON 结构，不判断对错。
