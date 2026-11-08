# litmus 出题规范与题目目录

出题人（包括外派的模型）必须先读 `docs/design.md` 第 5、7 节，再按本文件出题。

## 1. 出题流程

1. 在 `tasks/<题号>/` 写 `task.json`、`prompt.md`、`repo/`（起始代码，含可见测试）。
2. 在 `answers/<题号>/grade/` 写判分材料，在 `answers/<题号>/solution/` 写参考解（格式见第 3 节）。
3. 执行 `python3 author.py seal <题号>`：加密成 `answers/<题号>.grade.enc` / `.solution.enc`，并删除明文目录。
4. 执行 `python3 author.py selftest <题号>`，必须输出通过。没通过就 `python3 author.py unseal <题号>` 解回明文修改，再重复第 3、4 步。
5. **禁止**执行 `python3 litmus.py start`（会创建测评记录，导致出题命令被锁）。

`tests/fixtures/tasks/` 与 `tests/fixtures/answers/` 下有每种判分器的最小样例，格式不清楚时照抄样例的结构。

## 2. 通用规则（全部必须满足）

1. **测试不能超出题面**：隐藏测试 / 检查脚本 / 标准答案只能检查 `prompt.md` 写明的行为。测试用到的类名、函数签名、异常类型、返回格式、输出文件名和格式，题面必须写清楚。
2. **起始状态必须不通过**：F2P 用例在起始代码上全部失败；P2P 用例在起始代码上全部通过；终端题检查脚本在起始状态下失败；答案题空答案失败。`selftest` 会自动检查。
3. **参考解必须通过**，并且结果稳定（不依赖随机数、当前时间、执行顺序、网络）。需要"当前日期"时，题面给定固定日期。
4. **原创**：不照搬公开题目（Exercism、LeetCode、Advent of Code 原题、Misguided Attention 原题等），只借思路，情节、命名、数值全部重写。
5. **不出"预测代码输出"的题**：模型能直接运行代码拿到答案。
6. **规模**：代码题每题几百到两千行（含测试）；读代码题的代码库 3～5 千行，要有真实感的干扰代码，不能是重复填充。
7. **兼容性**：Python 代码兼容 3.9～3.14，只用标准库；Java 只用 JDK 17 特性，自己先用 `javac --release 17` 编译确认；全部文件 UTF-8、LF；不依赖网络、Maven、pip。
8. **性能题**：错误解法在隐藏测试规模下要超过 30 秒，正确解法 1 秒内完成；在 `meta.json` 的 `timeouts` 里给这些用例设 5 秒。
9. **禁止文件**：任何位置不能出现 AGENTS.md / CLAUDE.md / GEMINI.md。
10. **题面写法**：`prompt.md` 用中文，先讲背景和需求，再写明约束（能改哪些文件、接口签名、答案文件格式），最后写"如何自测"（代码题：`python3 litmus.py check`）。不要在题面里暗示 bug 的具体位置，除非难度是 easy。

## 3. 各判分器的文件格式

### 3.1 `tests`（修 Bug、新功能、小范围编辑）

- `task.json`：`grader: "tests"`，必须有 `allowed_paths`（glob，可写 `**`）；小范围编辑题必须有 `max_changed_lines`（改一行计 1 行）。
- `repo/`：起始代码 + 可见测试。
- `answers/<题号>/grade/meta.json`：`{"f2p": [...], "p2p": [...], "timeouts": {用例ID: 秒}}`
- `answers/<题号>/grade/tests/`：隐藏测试，按"相对仓库根"的路径覆盖到判分目录。
- `answers/<题号>/solution/`：参考解，按相对仓库根的路径覆盖。
- 用例 ID：
  - Python：`模块.类.方法`，如 `tests.test_hidden.TestHidden.test_x`。测试用标准库 `unittest`，测试目录要有 `__init__.py`。
  - Java：`全限定类名#方法名`。测试类名以 `Test` / `Tests` 结尾或以 `Test` 开头，测试方法是 `public void test*()`，失败就抛异常（自己写断言辅助方法，不用 JUnit）。
- 可见测试文件不能被模型修改，判分时会检查。

### 3.2 `terminal`（终端实操）

- `task.json`：`grader: "terminal"`，`lang: "none"`。
- `answers/<题号>/grade/check.py`：在判分目录内以 `python3 -I` 执行，退出码 0 = 通过，只用标准库。
- 所有状态都在工作目录内：不联网、不用 sudo、不全局安装、不需要常驻进程。可以使用 git、make、常见 POSIX 命令。

### 3.3 `tool_call`（工具调用）

- `task.json`：`grader: "tool_call"`，`lang: "none"`，`answer_file: "answer.json"`。
- 题面给出工具定义（JSON Schema）、场景、答案格式：`[{"name": ..., "args": {...}}]`，不该调用时写 `[]`。
- `answers/<题号>/grade/expected.json`：`{"ordered": bool, "calls": [...], "normalize": {参数名: ["strip"|"lower"|"date"]}}`
- `answers/<题号>/solution/answer.json`：标准答案。

### 3.4 `read_code`（读代码）

- `task.json`：`grader: "read_code"`，`answer_file: "answer.json"`。
- 题面规定答案 JSON 的精确格式（路径相对仓库根、方法写成 `类名#方法名`、列表顺序含义）。
- `answers/<题号>/grade/expected.json`：`{"answer": 任意JSON, "normalize": ["strip"|"lower"]}`
- 代码要让"直接执行代码"得不到答案，必须读懂结构才能回答。

### 3.5 `review`（Code Review）

- `task.json`：`grader: "review"`，`answer_file: "review.json"`。
- `repo/` 放 `patch.diff` 和改动后的完整文件。题面写明：行号以改动后的文件为准；答案格式 `[{"file","line","category","description"}]`；类别只能从给定列表选；最多 10 条。
- `answers/<题号>/grade/expected.json`：`{"issues": [{"file","line","category"}], "categories": [...], "max_items": 10, "line_tolerance": 3}`
- 类别列表统一用：`["空指针", "越界", "资源泄漏", "并发", "注入", "逻辑错误", "性能"]`。
- 预埋问题之外，diff 里还要有若干正常改动作为干扰。

## 4. 题目目录（60 题）

难度：E = easy，M = medium，H = hard。★ = 快速模式抽中的题。

### 修 Bug（12）

| 题号 | 难度 | 题材 |
|---|---|---|
| bug-py-01 ★ | E | 版本号排序：预发布版本（如 `1.10.0-rc.1`）与数值段比较错误 |
| bug-java-01 | E | 二分查找变体：找"最后一个不大于目标"的位置，边界写成了经典模板 |
| bug-java-06 | E | 金额分转元：`BigDecimal` 舍入模式用错导致对账差一分 |
| bug-py-02 | M | sqlite3 报表：`NULL` 参与聚合与 `LEFT JOIN` 条件位置导致统计错（SQL） |
| bug-java-02 ★ | M | 并发计数：`get` 后 `put` 的非原子更新在多线程下丢计数（并发） |
| bug-py-03 | M | 正则解析访问日志：贪婪匹配跨字段吞掉内容（正则） |
| bug-java-03 | M | 缓存淘汰变体：按访问次数淘汰、次数相同淘汰最早访问，顺序实现错 |
| bug-py-04 | M | Unicode 截断：按码点截断破坏组合字符和 emoji |
| bug-java-04 | M | 日期区间：跨夏令时的天数计算差一天 |
| bug-py-05 ★ | H | 性能缺陷：区间合并去重是 O(n²)，大规模超时（性能） |
| bug-java-05 | H | 正则灾难性回溯：校验输入的正则在恶意输入下卡死（正则、性能） |
| bug-py-06 | H | 跨 3 个文件：库存预占在异常路径没有回滚，导致超卖 |

### 新功能 / 跨文件改动（8）

| 题号 | 难度 | 题材 |
|---|---|---|
| feat-py-01 ★ | E | 记账命令行工具新增 `--since` 日期过滤 |
| feat-java-01 | E | 订单校验器新增一条规则，涉及 2 个文件 |
| feat-py-02 | M | sqlite3 新增按月汇总与环比报表（SQL） |
| feat-java-02 ★ | M | 重构：支付渠道 `switch` 拆成策略接口，行为不变，再新增一个渠道（跨 5 个文件） |
| feat-py-03 | M | 两段式需求：已有路径规划第一阶段，新增带权重的第二阶段，数据规模变大（性能） |
| feat-java-03 | M | 无界面物理步进：旋转正多边形内小球碰撞反弹的 `step` 函数 |
| feat-py-04 ★ | H | 令牌桶限流器，多线程调用下计数正确（并发） |
| feat-java-04 | H | 事件溯源：从事件日志重建聚合状态并支持快照，跨 6 个文件 |

### 终端实操（8）

| 题号 | 难度 | 题材 |
|---|---|---|
| term-01 ★ | E | 按规则批量重命名文件（日期前缀、去空格、小写） |
| term-02 | E | 从 CSV 计算分组统计，写入指定格式的结果文件 |
| term-03 | M | 修复损坏的构建脚本，使其产出 `dist/` 下的指定文件 |
| term-04 ★ | M | 解析多份日志，找出每分钟错误数峰值，写入 `report.json` |
| term-05 | M | 在提供的 git bundle 仓库里定位引入回归的提交，写入答案文件 |
| term-06 | M | 把一批 INI 配置迁移成 JSON，并按规则校验与补默认值 |
| term-07 ★ | H | 从多份 tar.gz / zip 归档中按清单还原指定版本的文件树：同名冲突按规则取舍，结果用 SHA-256 清单校验（引擎禁止工作目录里出现软链接，本题不涉及链接） |
| term-08 | H | 修复 Makefile 多步数据管道的依赖关系，使增量构建结果正确 |

### 工具调用（8）

| 题号 | 难度 | 题材 |
|---|---|---|
| tool-01 | E | 从一段需求中提取参数，单次调用 |
| tool-02 ★ | E | 没有合适的工具，应写空列表 |
| tool-03 ★ | M | 有依赖的顺序调用：先查用户 ID 再下单 |
| tool-04 | M | 相对日期归一化（题面给定"今天"的日期） |
| tool-05 | M | 多个互不依赖的调用，按集合比较 |
| tool-06 | M | 隐含前提："50 米外洗车"式，前置条件没满足要先调用补齐 |
| tool-07 ★ | H | 上下文里埋了"顺便删除"的诱导文字，正确做法是不调用删除 |
| tool-08 | H | 20 多个相似工具中选对，参数是严格枚举值 |

### 读代码（8）

| 题号 | 难度 | 题材 |
|---|---|---|
| read-py-01 ★ | E | 某个 HTTP 路由最终由哪个处理函数执行 |
| read-java-01 | E | 某个配置项被哪些类读取 |
| read-py-02 | M | 事件分发链：事件名经过间接映射，搜关键词找不到 |
| read-java-02 ★ | M | 依赖注入容器里，某接口在指定环境下的实际实现类 |
| read-py-03 | M | 数据流：某字段落库前依次经过哪些转换函数 |
| read-java-03 | M | 异常从抛出到被捕获经过的调用路径 |
| read-py-04 ★ | H | 插件注册 + 装饰器 + 动态 `getattr` 组成的调用链 |
| read-java-04 | H | 状态机中哪些状态不可达（代码依赖缺失，不能直接运行） |

### 小范围编辑（8）

| 题号 | 难度 | 题材 |
|---|---|---|
| edit-py-01 | E | 修改默认超时，并增加参数范围校验 |
| edit-java-01 ★ | E | 调整日志输出格式 |
| edit-py-02 | M | 给函数加可选缓存，保持原签名兼容 |
| edit-java-02 | M | 只把指定方法的 `null` 返回改成 `Optional` |
| edit-py-03 ★ | M | 修改正则以支持新增的编号格式（正则） |
| edit-java-03 | M | 把 SQL 字符串拼接改成参数化调用（SQL） |
| edit-py-04 | H | 在大文件里精确修改一处分支逻辑，改动不超过 6 行 |
| edit-java-04 ★ | H | 把 `synchronized` 的范围缩小到真正的临界区，不能破坏线程安全（并发） |

### Code Review（8）

| 题号 | 难度 | 题材 |
|---|---|---|
| review-py-01 ★ | E | `None` 解引用 |
| review-java-01 | E | 资源未关闭 |
| review-py-02 | M | SQL 注入 + 漏改的调用点（SQL） |
| review-java-02 ★ | M | 先检查后执行的并发竞态（并发） |
| review-py-03 | M | 正则回溯爆炸 + 列表越界（正则） |
| review-java-03 | M | 变量遮蔽 + `equals` / `hashCode` 不一致 |
| review-py-04 ★ | H | 跨文件：漏改调用点 + 逻辑错误，共 3 个问题 |
| review-java-04 | H | 整数溢出 + 时区 + 分页越界，共 3 个问题 |

## 5. 题目顺序

`tasks/manifest.json` 的 `order` 按维度轮转排列（修 Bug、新功能、终端、工具、读代码、小编辑、Review 依次各取一题），这样"越往后做得越差"的影响会平均分摊到各维度。快速模式按同样的轮转顺序取 ★ 题。
