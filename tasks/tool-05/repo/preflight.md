# 发布前就绪检查清单

请依据 `status_board.json` 中各检查项的当前状态：
- 仅针对 `status == "pending"` 的检查项执行对应操作（缓存预热调用 `warm_edge_cache`、DNS 校验调用 `verify_dns_propagation`、开关同步调用 `sync_feature_flags`）。
- 对于 `completed` 或 `cancelled` 状态的项目，一律不要调用工具。
