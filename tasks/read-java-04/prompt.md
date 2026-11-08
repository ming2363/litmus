# read-java-04: 闸口状态机里到不了的状态

## 背景

闸口作业单的状态登记在 `gatepass.sm`。仓库没有 `gatepass.external.TideClock`，`Machine.build` 不能直接编译运行。`TideClock.touch` 不登记边，也不改变守卫。

请列出从 `PassState.DRAFT` 出发走不到的枚举常量。

## 判定规则

只沿同时满足这些条件的边：

1. 边是 `Machine.build` 在当前源码常量下真正调用到的登记器加进去、并且最后还留在边表里的。
2. `if` 的条件是源码里的布尔常量，按这个常量判断登记器是否执行。
3. 先 `add` 再被 `remove` 掉的边不算。注释里的 `add` 不算。
4. 守卫是 `ConstantGuards.NEVER` 的边不能走。`ConstantGuards.ALLOW` 可以走。
5. 起点是 `DRAFT`。枚举里声明了、但这样走不到的常量都要列出。

顺序与 `PassState` 枚举声明顺序一致。

## 答案

写入工作目录根的 `answer.json`：

```json
{"initial": "DRAFT", "unreachable": ["STATE"]}
```

## 如何自测

执行 `python3 litmus.py check`。该命令只检查 JSON 结构，不判断对错。
