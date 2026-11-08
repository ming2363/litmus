# 变更排期与窗口查询请求

基准日期：今天为 **2026-11-08（星期日）**。

请依次完成以下两步操作：
1. 先调用 `query_blackout_windows` 查询冻结窗口：`start_date` 为**上个月（2026 年 10 月）的最后一天**，`end_date` 为**后天**（即今天往后推 2 天）。
2. 再调用 `schedule_maintenance` 为集群 `orders-pg-primary` 预约维护：
   - `target_date` 定在 **2026 年 11 月的第 3 个星期一**；
   - `backup_date` 定在 **从 `target_date` 起往后推 15 天**（即 `target_date + 15 天`）。
