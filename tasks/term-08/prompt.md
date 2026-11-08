# term-08: 修复 Makefile 多步数据管道增量依赖

## 背景与需求
工作目录中有一个基于 `Makefile` 的四阶段 ETL 数据处理管道，但当前 `Makefile` 的规则与依赖关系存在多处错误，导致首次全量构建或局部文件变动后的增量构建结果不正确。
请修复工作目录下的 `Makefile`（**不要修改** `data/` 和 `scripts/` 下的任何文件），并运行 `make` 生成完整且正确的构建产物。

## 管道结构与依赖规范
1. **输入文件**：
   - 分片数据：`data/shards/*.csv`（当前含 `alpha.csv`、`beta.csv`、`gamma.csv`）
   - 共享映射表：`data/lookup/currency_rates.json`、`data/lookup/region_map.json`
   - 处理脚本：`scripts/clean_shard.py`、`scripts/enrich_shard.py`、`scripts/aggregate.py`、`scripts/render_report.py`
2. **构建阶段与严格依赖关系**：
   - 阶段 1（`stage/cleaned/<name>.csv`）：由对应 `data/shards/<name>.csv` 与 `scripts/clean_shard.py` 生成（命令格式：`python3 scripts/clean_shard.py <input_csv> <output_csv>`）。
   - 阶段 2（`stage/enriched/<name>.json`）：由对应 `stage/cleaned/<name>.csv`、两份 `data/lookup/*.json` 与 `scripts/enrich_shard.py` 生成（命令格式：`python3 scripts/enrich_shard.py <cleaned_csv> data/lookup/currency_rates.json data/lookup/region_map.json <output_json>`）。
   - 阶段 3（`output/summary.json`）：聚合所有分片的 `stage/enriched/<name>.json`，并依赖 `scripts/aggregate.py`（命令格式：`python3 scripts/aggregate.py -o output/summary.json <所有 enriched json>`）。
   - 阶段 4（`output/report.tsv`）：由 `output/summary.json` 与 `scripts/render_report.py` 生成（命令格式：`python3 scripts/render_report.py output/summary.json output/report.tsv`）。
3. **增量构建与可靠性要求**：
   - `make`（默认目标 `all`）在经过 `make clean` 清理后，**单次执行**即可一次性构建全部 4 个阶段，产出 `output/summary.json` 与 `output/report.tsv`。
   - `make clean` 必须彻底清理 `stage/` 与 `output/` 目录（无论工作目录中是否恰巧存在名为 `clean` 或 `all` 的文件，目标均需正常生效）。
   - 增量构建无误触发、无漏触发：
     - 连续两次执行 `make`，第二次不得重建任何目标文件；
     - 仅修改单个原始分片（如 `data/shards/alpha.csv`）时，仅重建该分片对应的 `cleaned`/`enriched` 目标及下游 `output/*`，不得重建其他分片（`beta`、`gamma`）的产物；
     - 仅修改共享查找表（如 `data/lookup/currency_rates.json`）时，不得重建 `stage/cleaned/*`，但必须重建所有 `stage/enriched/*` 及下游 `output/*`；
     - 修改任一阶段脚本（如 `scripts/clean_shard.py`）时，必须触发该阶段及全部下游目标的重建。
   - 支持并发构建（`make -j2`）且命令失败时不能留下损坏的目标文件。

## 如何自测
- 在工作目录先后测试 `make clean && make`、`make`（二次空转）、`make clean && make -j2`，以及 `touch` 单个分片/查找表/脚本观察实际重建的命令集合。
- 完成后可执行 `python3 litmus.py check` 检查工作目录无违规符号链接。
