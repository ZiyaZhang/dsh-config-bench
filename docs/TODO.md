# 还缺什么

按能不能开跑排序。

## 挡住开跑的

- [ ] 跑批程序：从 `subagent-limits-eval/code/dsec_matrix_v6.py` 移过来，去掉开发机路径和内网端点，改成读 `configs/*.yaml` 和 `tasks/*/task.yaml`。
- [ ] 指标：移 `run_metrics.py`，输出字段改成 `docs/design.md` 里的 schema。
- [ ] 判分资产（都在开发机 `/weka-hg/.../dsec-exp` 上，等机器能登）：
  - [ ] `exercises-24`：判分用的完整 Python 测试（工作区里只有部分测试）。
  - [ ] `toolkit-xl`：3,737 个隐藏测试。
  - [ ] `chain-16`：16 步的答案键。

## 开跑之后

- [ ] 办公报告题的事实清单：现在每题 60–100 条，补到两题各 100 条以上，并标出哪些条目会随时间失效。
- [ ] 适配器：先做 DeepResearch Bench II 和 WideSearch 两个，题面不进仓库，用的人自己取。
- [ ] 判分校验搬过来：自判两遍、换模型复判、加无关正确文字、插看似合理的错误事实。
- [ ] 行为标注搬过来：十项行为清单和再派活分类，标注结果带 `source: model_label`。
- [ ] 题太少：办公类只有 2 道，噪声大（上一轮实测单次运行标准差约 7 分，效应 2–3 分），补到 15–20 道。
