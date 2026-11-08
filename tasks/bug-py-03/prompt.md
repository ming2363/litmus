# 修复访问日志解析

结算服务把一行行的访问日志拆成字段。消息正文里如果再出现 `duration_ms=` 或 `key=`，当前的正则会跨过真正的字段，把正文前半段吞进事件名。

## 行格式

非空行必须完整匹配：

```text
<date> <level> <event> duration_ms=<整数> key=<键> message=<正文>
```

- `date`、`event`、`key` 都是不含空白的一段。
- `level` 只能是 `DEBUG`、`INFO`、`WARN`、`ERROR`。
- `duration_ms` 是十进制非负整数，解析成 `int`。
- `message` 是 `message=` 之后直到行尾的全部内容，可以为空，可以包含空格。
- 正文里允许出现 `duration_ms=`、`key=` 和 `message=` 这些字样。字段边界以第一个 `duration_ms=` 和紧随其后的 `key=` 为准，不能改用正文里更靠后的同名片段。

例如：

```text
2026-11-08T01:02:03Z ERROR checkout.pay duration_ms=15 key=order.created message=retry duration_ms=999 key=other message=failed
```

解析结果是 `event=checkout.pay`，`duration_ms=15`，`key=order.created`，`message` 为 `retry duration_ms=999 key=other message=failed`。

## 接口

`accesslog.parser.parse_line(line)` 返回字典，键为 `date`、`level`、`event`、`duration_ms`、`key`、`message`。无法匹配时抛出 `ValueError`，消息里包含原始行。

`parse_lines(text)` 按换行拆开，忽略空行和只含空白的行，返回解析结果列表。某一行非法时抛出 `ValueError`。

`accesslog.summary.by_level(text)` 返回 `{级别: 行数}`，只包含实际出现过的级别。它应该跟着解析结果走。

只修改 `accesslog/` 下的 Python 文件，不要改测试。

## 如何自测

`python3 litmus.py check`
