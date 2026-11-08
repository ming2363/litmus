# 生产发布前置条件规范

执行 `deploy_release` 前，以下条件必须全部为 `true`：
1. 目标版本 `image_built` 为 `true`（否则先调用 `build_image`）；
2. 目标版本 `smoke_tests_passed` 为 `true`（否则先调用 `run_smoke_tests`）；
3. 目标集群 `config_synced` 为 `true`（否则先调用 `sync_cluster_config`）；
4. 目标版本 `artifact_signed` 为 `true`（否则先调用 `sign_artifact`）；
5. 目标集群 `deploy_lock_held` 为 `true`（否则先调用 `acquire_deploy_lock` 申请锁）。

执行规范：
- 已为 `true` 的条件不得重复调用前置工具；
- 若同时需要补齐产物签名和集群部署锁，**必须先签名产物（`sign_artifact`），再申请部署锁（`acquire_deploy_lock`），最后再执行发布（`deploy_release`）**。
