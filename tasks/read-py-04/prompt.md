# read-py-04: 潮汐对账的实际调用链

## 背景

潮汐插件用装饰器登记。对外操作名和类上的方法名不是同一串文字，方法外面还有包装。

请给出操作 `tide.reconcile` 的实际调用链。能力集合只认 `tidekit.runtime.caps.ACTIVE_CAPS` 里的字面量。

## 判定规则

按运行时进入顺序，只列入下面这些，不要多也不要少：

1. `tidekit.runtime.entry.Entry#invoke`
2. `invoke` 直接调用的 `Resolver#select`
3. `invoke` 直接调用的 `Resolver#verb_for`
4. 最终业务方法外面的装饰器，由外到内。写装饰器的函数，格式 `模块.函数名`。不要写装饰器内部的 `wrapped`。
5. `getattr` 真正取到的业务方法，格式 `模块.类名#方法名`

不要列入 `str.split`、`getattr`、插件构造、能力字典本身，也不要展开 `select` 和 `verb_for` 的内部调用。

选择规则以 `Resolver` 源码为准：家族相同、所需能力在 `ACTIVE_CAPS` 中全为真的登记才保留；优先级数字小的获胜；数字相同再比插件 id 的字典序。方法名是「类上的阶段前缀 + 下划线 + 动作别名的词干」。

## 答案

写入工作目录根的 `answer.json`：

```json
{"operation": "tide.reconcile", "chain": ["..."]}
```

## 如何自测

执行 `python3 litmus.py check`。该命令只检查 JSON 结构，不判断对错。
