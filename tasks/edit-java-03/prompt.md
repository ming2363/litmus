# edit-java-03: 将 SQL 字符串拼接重构为参数化调用

## 背景与需求

当前仓库是一个工单查询与更新持久层模块（`src/com/litmus/ticket/`），包含：

- `Ticket.java`：不可变工单记录模型；
- `InMemoryTicketDb.java`：内置标准 `java.sql` 接口的内存关系数据库引擎（支持 `Statement`、`PreparedStatement`、参数绑定、`WHERE`、`ORDER BY`、`LIKE ... ESCAPE '\\'`）；
- `TicketDao.java`：工单数据访问对象。

目前 `TicketDao.java` 的三个方法均直接通过 `conn.createStatement()` 与字符串拼接构造 SQL，存在严重的 SQL 注入与特殊字符（单引号 `'`、`LIKE` 通配符 `%` / `_`）破坏语句问题，且未保证 JDBC 资源关闭。

请仅修改 `src/com/litmus/ticket/TicketDao.java`，完成以下重构要求：

1. **全面改用参数化查询**：
   - `findByAssigneeAndStatus(Connection conn, String assignee, String status)`、`searchByTitleKeyword(Connection conn, String keyword)`、`updatePriorityAndNote(Connection conn, int id, int newPriority, String note)` 均须停止使用 `Statement` 与字符串拼接用户输入，改用 `conn.prepareStatement(...)` 与 `?` 占位符参数绑定。
   - 不得更改 `TicketDao` 对外方法名、参数类型、返回类型与原有空值/范围校验（若原来会抛出 `SQLException` 或 `IllegalArgumentException` 的入参场景保持一致；若输入 `null` 保持原有处理或空校验一致）。
2. **`LIKE` 模糊匹配转义**：
   - `searchByTitleKeyword(Connection conn, String keyword)` 须实现**区分大小写**的标题字面子串包含匹配。
   - 当 `keyword` 中包含 `\`、`%`、`_`、单引号 `'` 等字符时，必须作为普通字面字符匹配（不得被当作 `LIKE` 通配符或破坏 SQL 语法）。建议配合 `WHERE title LIKE ? ESCAPE '\' ORDER BY id ASC` 并对 `\`、`%`、`_` 转义后绑定 `"%" + escaped + "%"`。
   - `keyword` 为 `null` 或空串时维持原有行为（`null` 抛 `IllegalArgumentException`，`""` 匹配所有标题或按原语义返回——注：`LIKE '%%'` 匹配全部非空标题）。
3. **资源正确释放**：
   - 使用 `try-with-resources` 确保打开的 `PreparedStatement` 与 `ResultSet` 在方法返回或抛出异常时都被正常关闭。

## 约束条件

- 只允许修改 `src/com/litmus/ticket/TicketDao.java`。
- **改动行数上限 (`max_changed_lines`)：`60` 行**。
- 不得修改 `Ticket.java`、`InMemoryTicketDb.java` 或可见测试文件 `TicketDaoPublicTest.java`。
- 仅使用 JDK 17 标准库（`java.sql.*` 等），无第三方依赖；全部文件 UTF-8 编码、LF 换行。

## 如何自测

在工作目录执行以下命令运行可见测试：

```bash
python3 litmus.py check
```
