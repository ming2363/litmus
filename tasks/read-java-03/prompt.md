# read-java-03: 过期预占异常的调用路径

## 背景

单笔确认会在代数不一致时抛出 `holdledger.error.StaleReservationException`。它是受检异常。

请列出从抛出该方法，到 `holdledger.api.HoldApi#confirmHold` 这条链上第一个捕获它的方法为止的路径。

## 判定规则

1. 只看 `confirmHold` 调用下去的那条链，不要算 `replay`、批量接口或导入任务。
2. 顺序是从抛出语句所在的方法开始，沿调用栈向外，直到捕获该异常的方法，两端都要列入。
3. 中间没有捕获它的方法也要列入。捕获子句写的是别的异常类型、接不住它的，不算捕获点。
4. 不列入异常构造方法。
5. 方法写成 `包.类名#方法名`。

## 答案

写入工作目录根的 `answer.json`：

```json
{
  "exception": "holdledger.error.StaleReservationException",
  "entrypoint": "holdledger.api.HoldApi#confirmHold",
  "path": ["包.类名#方法名"]
}
```

## 如何自测

执行 `python3 litmus.py check`。该命令只检查 JSON 结构，不判断对错。
