# Markdown 摘录台账

Python-Markdown 3.9 需要一个新扩展：把文档里圈出的片段登记成摘录，正文仍留在原处参与这一篇的解析，调用方可以在转换之后拿到每条摘录的原文和它在最终输出里的 HTML。

只修改 `markdown/` 包中的源码。测试不要改。

## 加载

扩展的短名是 `excerpt`，模块是 `markdown.extensions.excerpt`，类是 `ExcerptExtension`，并提供 `makeExtension(**kwargs)`。用 Markdown 已有的扩展加载方式即可：短名、模块路径、`模块:类`、类实例，配置字典的键与 `extensions` 列表里的那个字符串相同。

配置项 `wrapper_class` 默认是空字符串。空字符串表示不额外包裹。非空时，这条摘录在输出里包进 `<div class="配置值" id="摘录标识">`。属性的转义和排列顺序跟序列化器对其它元素的处理一样。

## 语法

开栏独占一行：行首 0 到 3 个空格，然后是 `:::excerpt`、至少一个空格、标识，行尾可以有空格。标识由字母开头，后面只含字母、数字、下划线和连字符，大小写敏感。不符合这一行的文本不是开栏。

收栏独占一行：行首 0 到 3 个空格，然后只有 `:::`，行尾可以有空格。收栏只关闭当前最内层。

开栏可以出现在一个块的中间，它前面的文本先按原样解析。摘录在块解析阶段识别。预处理器已经拿走的围栏代码，以及按现有缩进规则成为代码块的内容，都不会再被当成摘录。

开栏和收栏之间是正文。开栏行自己有几个前导空格，正文每一行就去掉几个前导空格，再交给解析器；空行去掉这些空格后仍是空行，缩进不够的行保持原样。这样和开栏对齐的正文不会因为那一点缩进变成代码块。没有收栏时，正文延伸到当前这个父结构的末尾：文档顶层就是文末；写在列表项或引用里面时，停在该项或该引用的末尾，不把后面的兄弟块吞进去。

开栏和收栏只起分块作用，不改变输出的其它任何内容。没有 `wrapper_class` 时，把每个开栏和收栏都换成空行（在列表项或引用里，只去掉这一行的栏标记，保留列表标记或 `>`），正文按上面的规则去掉缩进，用同样的配置转换这份文档，除了 `{@标识}` 变成的链接，得到的输出与原文档逐字相同，标签之间的换行也一样。有 `wrapper_class` 时，再把每条摘录正文的各块放进那个 `div`，换行排版和其它 `div` 一样。

正文用当前这一个 Markdown 实例的块解析器就地解析，不要另建实例，也不要先把解析器的状态清掉。脚注、目录、引用定义、属性列表因此都落在同一篇文档上。输出格式仍由这个实例的 `output_format` 决定。

行内 `{@标识}` 使用同一套标识字符。它在全部块解析完成之后才解析，所以可以指向后面才出现的摘录。能对上标识时输出 `<a class="excerpt-ref" href="#标识">标识</a>`，链接文字就是标识本身。对不上的保留原文，和处理未定义的引用式链接一样。行内代码和反斜杠转义仍按它们现有的优先级先处理。

## 台账

加载扩展后，实例有 `excerpts` 和 `get_excerpt(标识)`。`excerpts` 的每一项是 `markdown.extensions.excerpt.Excerpt`，属性是 `id`、`html`、`source`。

- `source` 是去掉开栏那一层前导空格之后、开栏与收栏之间的正文。被空行分开的块，中间仍保留一个空行。开栏行和收栏行本身不在 `source` 里。内层摘录的标记行留在外层的 `source` 里。没有正文时 `source` 是空字符串。
- `html` 是这条摘录在最终输出里的对应片段，去掉首尾空白。开栏和收栏不出现在输出里。有 `wrapper_class` 时，片段包含那个 `div`；没有时，就是正文各块自己的 HTML。会在整篇文档里搬家的内容，只留在它最终所在的位置，不因为曾经写在摘录里就算进 `html`。
- 顺序就是开栏出现的顺序，外层先于它内部的开栏。标识可以重复，每次出现都收录。`get_excerpt` 返回该标识的第一条；没有则返回 `None`。

每一次 `convert` 都用这一次的结果替换台账，没有摘录时台账是空列表。`reset()` 之后台账也是空的。不要因此清掉其它扩展自己的状态。

## 示例

基本摘录：

```markdown
:::excerpt intro

hello

:::
```

输出 `<p>hello</p>`。`excerpts[0]` 的 `id` 是 `intro`，`source` 是 `hello`，`html` 是 `<p>hello</p>`。`get_excerpt('intro')` 就是这一条。

向前引用：

```markdown
see {@intro}

:::excerpt intro

hello

:::
```

输出：

```html
<p>see <a class="excerpt-ref" href="#intro">intro</a></p>
<p>hello</p>
```

`wrapper_class` 为 `callout` 时，基本摘录的输出是：

```html
<div class="callout" id="intro">
<p>hello</p>
</div>
```

`html` 与整段输出相同，`source` 仍是 `hello`。

开栏带两个前导空格：

```markdown
  :::excerpt intro

  hello

  world

  :::
```

`source` 是 `hello\n\nworld`，输出是：

```html
<p>hello</p>
<p>world</p>
```

嵌套：

```markdown
:::excerpt outer

before

:::excerpt inner

inside

:::

after

:::
```

外层在前。外层 `source` 是：

```text
before

:::excerpt inner

inside

:::

after
```

外层 `html` 是：

```html
<p>before</p>
<p>inside</p>
<p>after</p>
```

内层 `source` 是 `inside`，内层 `html` 是 `<p>inside</p>`。

## 如何自测

在题目仓库根目录执行 `python3 litmus.py check`。
