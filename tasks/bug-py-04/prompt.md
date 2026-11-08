# 修复摘要截断把字符切碎

卡片摘要目前按 Unicode 码点截断。组合附加记号、国旗、肤色和零宽连接符粘起来的 emoji 会被从中间切开。截断必须按扩展字素簇（用户看到的一个字符）进行。

## 字素规则

按下面的顺序切分，后面的规则不再改写前面已经切好的簇：

1. `CR LF`（`U+000D` 后接 `U+000A`）是一个簇。单独的回车或换行各是一个簇。
2. 区域指示符（`U+1F1E6` 到 `U+1F1FF`）两两成对，是一个簇。落单的一个单独成簇。区域指示符不和后面的零宽连接符粘在一起。
3. 其他情况从一个码点开始，再尽量向后吸收：
   - 变体选择符 `U+FE0E`、`U+FE0F`
   - 肤色修饰符 `U+1F3FB` 到 `U+1F3FF`
   - Unicode 类别为 `Mn` 或 `Me` 的组合记号
   - 然后可以重复：零宽连接符 `U+200D` 加上后面一个码点，再吸收上一组延伸符。行尾多余的 `U+200D` 留在当前簇里。

除此之外，每个码点单独成簇。不处理韩文音节的特殊拼接。

## 接口

`snippets.truncate.grapheme_length(text)` 返回簇的个数。

`snippets.truncate.truncate_graphemes(text, limit)` 返回前 `limit` 个完整簇组成的前缀。簇数不超过 `limit` 时原样返回。`limit` 为 0 时返回空字符串。

- `text` 不是 `str`，或 `limit` 不是 `int`（`bool` 也不行）时抛出 `TypeError`。
- `limit < 0` 时抛出 `ValueError`，消息里包含 `limit`。

例子：`é` 写成 `e` 加 `U+0301` 时，限制 1 必须保留重音。`🇨🇳` 限制 1 必须保留整面国旗。`👨‍👩‍👧` 限制 1 必须保留整个家庭符号。`👍🏽` 限制 1 必须保留肤色。

`snippets.preview.card(title, body, title_limit, body_limit)` 返回字典 `{"title": ..., "body": ...}`，两个字段分别用上面的函数截断。

只修改 `snippets/` 下的 Python 文件，不要改测试。

## 如何自测

`python3 litmus.py check`
