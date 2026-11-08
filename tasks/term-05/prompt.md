# term-05: 在 git bundle 中定位回归提交

## 背景与需求
工作目录中提供了一个 Git Bundle 文件 `ledger.bundle`（包含完整提交历史、分支 `main` 以及基线标签 `v1.0.0`）。
仓库中的核心计费函数 `ledger.proration.compute_prorated_charge` 在标签 `v1.0.0` 时对如下订阅降级场景能返回正确结果，但当前 `main` 分支的 `HEAD` 返回了错误结果（注意：仓库自带的现有单元测试未能覆盖此边界场景，在 `main` 上仍会通过）：

- 复现调用：
  ```python
  compute_prorated_charge(
      old_plan_cents=12000,
      new_plan_cents=6000,
      used_days=10,
      total_days=30,
      credit_cents=500,
      discount_pct=0,
      tax_bps=800,
  )
  ```
- 期望返回（`v1.0.0` 的正确行为）：
  `{"payable_cents": 0, "carry_credit_cents": 4500, "tax_cents": 0}`

请从 `ledger.bundle` 检出仓库到工作目录内的子目录，通过比对与定位（如 `git bisect`），找出从 `v1.0.0` 到 `main` 之间**第一个**引入该回归的提交，并将结果写入工作目录根下的 `culprit.json`。

## `culprit.json` 输出格式
必须为包含且仅包含以下两个字段的 JSON 对象：
```json
{
  "commit": "<40位完整小写提交哈希>",
  "changed_file": "<该提交修改的相对文件路径>"
}
```

## 如何自测
- 在检出的仓库内使用 `git show <commit>` 核实该提交的 40 位完整哈希与修改的文件路径，确认其前一个提交该用例通过、该提交开始该用例失败。
- 完成后可执行 `python3 litmus.py check` 检查工作目录无违规符号链接。
