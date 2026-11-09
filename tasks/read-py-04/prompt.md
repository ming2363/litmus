# 冷箱夜班审计实际走了哪条调用链

`harborpipe.gate.Gate.invoke("lane.reefer.audit")` 处理这一次操作时，运行时依次进入了哪些调度帧？把答案写入工作目录根的 `answer.json`：

```json
{"operation": "lane.reefer.audit", "chain": ["包.模块.类名#方法名"]}
```

`operation` 固定为 `lane.reefer.audit`。`chain` 从先进入的帧排到后进入的帧。帧写成源码里的定义名：方法是 `包.模块.类名#方法名`，函数是 `包.模块.函数名`。定义在函数内部的函数，限定名里保留 `<locals>`。

链按下面的槽位填写：

1. `harborpipe.gate.Gate#invoke`
2. 到 5. `invoke` 方法体里直接调用的那四个 `harborpipe` 方法，顺序与源码里的调用顺序一致
6. 上述调用都返回之后，业务方法被调用前实际进入的包装体。包装体指这一层的 `__call__`，或包装函数自己。按先进入的顺序逐个写入
7. 业务方法本身。链在这一帧结束

## 如何自测

执行 `python3 litmus.py check`。它只检查 JSON 结构，不判断调用链对不对。
