# read-java-02: 备用环境下的计费实现

## 背景

引航计费有多套实现，由环境名选择。仓库没有 `pilotage.external.HarborClock` 的源码，因此 `Selector` 不能直接编译运行。该类的 `sync` 不参与绑定判断。

请给出接口 `pilotage.billing.BillingGateway` 在环境 `harbor-standby` 下被选中的实现类。

## 判定规则

以 `pilotage.container.Selector#choose` 的源码为准，数据来自 `ProfileData` 和 `Props.load` 会读到的那一个 properties 文件：

1. 只保留 profile、接口名都相同的绑定。
2. `conditionKey` 为 null 的绑定无条件保留。
3. `conditionKey` 不是 null 时，对应属性值必须恰好是 `true` 才保留。缺键或其他文本都丢弃。
4. 剩下的按 `priority` 从小到大，相同再按实现类全限定名的字典序，取第一条。
5. 文件名不是 `<profile>.properties` 的配置不要读。

## 答案

写入工作目录根的 `answer.json`：

```json
{"interface": "pilotage.billing.BillingGateway", "profile": "harbor-standby", "implementation": "全限定类名"}
```

## 如何自测

执行 `python3 litmus.py check`。该命令只检查 JSON 结构，不判断对错。
