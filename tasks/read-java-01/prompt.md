# read-java-01: 哪些类读取了探针过期分钟

## 背景

冷链仓用 `coldvault.config.ConfigStore` 保存字符串配置。请找出源码里真正读取键 `vault.probe.stale.minutes` 的类。

## 判定规则

同时满足下面几条才算读取：

1. 在某个类的方法体里调用了 `ConfigStore` 的 `get`、`getInt` 或 `getLong`。
2. 这次调用的第一个实参是字符串字面量（相邻字面量直接拼在一起也算），拼完后的文本恰好是该键。
3. 只出现在注释、日志或告示文案里的同名文字不算。
4. 只声明常量、自己不调用 `ConfigStore` 的类不算。
5. 读取其他键的类不算。

类名写全限定名，按 Unicode 码点升序排列，不要重复。

## 答案

写入工作目录根的 `answer.json`：

```json
{"key": "vault.probe.stale.minutes", "readers": ["全限定类名"]}
```

## 如何自测

执行 `python3 litmus.py check`。该命令只检查 JSON 结构，不判断对错。
