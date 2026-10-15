# 设计

题 × 配置 × 重复：每格跑几次，报质量、花费、时长和一组行为计数。模型固定，变的是配置。

## 与 dsh-dev-bench 的关系

组里的 `deepseek-harness/dsh-dev-bench` 做的是另一件事：一个 bench 只允许一道题，DSH 的配置写死在 executor 里，因子都是"改代码库"（注释、git 历史、测试），运行顺序是确定性轮转，没有 pass@k。它的 `Offline()` setup 证明了"按 Run 改 DSH profile"这条路可行，但 setup 对所有 Run 全量生效，不参与交叉，所以比不了配置。

对策：这边独立迭代，**字段名照抄它**，将来整块并过去只改两个文件（`executors/dsh/config.ts` 的 profile 参数、`executors/dsh/index.ts` 的 `prepare()` 从 `context.factors` 读档位）。对应关系在本文末尾。

## 题：`tasks/<task_id>/task.yaml`

一题一目录，目录里就是这道题的全部材料。

| 字段 | 说明 |
|---|---|
| `task_id` `version` | 题改了就升 version，结果里记的是哪一版 |
| `title` `category` `tags` `difficulty` `author` `created_at` | 元数据 |
| `canary` | 防训练集污染的标记串，照抄 terminal-bench |
| `web` | 这道题准不准上网 |
| `workspace` | `{kind: empty}` 或 `{kind: tar, path: ...}` 或 `{kind: repo, url, revision}` |
| `deliverable` | `{kind: file, name, min_bytes}` 或 `{kind: changed_files, files_from}` |
| `max_agent_timeout_sec` / `max_test_timeout_sec` | agent 的时限和判分的时限分开 |
| `expert_time_estimate_min` | 人做要多久，用来排标注预算 |
| `variants` | 同一道题的档（例如限时 180 秒/120 秒），不是配置 |
| `scorers` | 列表，每条 `{name, type, ...}`；`type` 对应 `scorers/` 里注册的名字 |
| `aggregate` | 多个 scorer 怎么合：`mean`（默认）、`min`、`weighted` |

金标、清单、文件清单一律放 `expected/`，方便一次性剥掉再发题。

## 配置：`configs/<config_id>.yaml`

`config_id`（短名，像 `d1k8`）、`title`、`description`、`default`（标出哪个是 DSH 默认）、`patch`（落到 DSH 的 cordis patch 片段）、可选 `tool_description_suffix`（改工具说明的对照组）。

配置是**被比较的轴**，所以它必须落盘进每条结果，不能只出现在命令行里。

## 单次运行：`runs/<run_id>/<task_id>/<trial_name>/result.json`

`trial_name = {task_id}.{config_id}.{attempt}-of-{n}.{run_id}`。

- 标识：`run_id` `task_id` `task_version` `config_id` `variant_id` `attempt`
- 状态：`status` ∈ `passed` | `failed` | `invalid` | `prepared`，`failure_mode` ∈ `none` `agent_timeout` `test_timeout` `context_length_exceeded` `transport` `rate_limit` `empty_response` `crash_at_exit` `no_deliverable` `unknown`
- 判分：`score`、`resolved`、`scorer_results: {name: {value, passed, reason, detail, source}}`
- 用量：`usage{input_tokens, input_tokens_cache_read, input_tokens_cache_write, output_tokens, reasoning_tokens, total_tokens, request_count}`、`cost{model_cny, search_cny, total_cny, price_table_version}`
- 时间：三对起止时间戳 `trial_started_at/ended_at`、`agent_started_at/ended_at`、`test_started_at/ended_at`
- 行为：`behaviour{n_agents, n_spawn_calls, n_denied_depth, n_denied_cap, peak_concurrency, max_depth, n_tool_calls, root_tool_share, kids_after_answer}`，每项带 `source: script`
- 环境：`dsh_version` `model` `effort` `config_hash` `image` `commit_hash`
- 原始：`transcript_path`（存路径，不内联）

`invalid` 的判定照抄 dsh-dev-bench：DSH 的 stderr 匹配到 `^dsh: (EMPTY_RESPONSE|RATE_LIMIT|SERVER|TIMEOUT|TRANSPORT):` 就是基础设施故障，不进分母。

## 一批：`runs/<run_id>/results.json`

`config` 块记 `{run_id, started_at, ended_at, tasks, configs, n_attempts, seed, order, commit_hash, run_command}`；`per_config` 每个配置一行：`{n_valid, n_resolved, resolved_ids, unresolved_ids, excluded_ids, mean_score, pass_hat_k, cost_cny, duration_p50}`。计数一律配 id 列表（照 SWE-bench），顶层随时可以从各 `result.json` 重建（照 terminal-bench）。

## 判分

接口在 `scorers/__init__.py`：`score(trial, task, spec) -> Score`，`Score{value, passed, reason, detail, source}`。

- 默认确定性：事实清单、隐藏测试、逐项精确匹配。
- LLM 判分是**可选的一个 scorer**，判分模型用 role 在运行时绑定（`--role grader=...`），给多个就各判一遍——"换模型复判"因此是一个配置项，不是另一套脚本。
- **判不了返回 `value=None`**，不要返回 0。多个 scorer 各出一个分再按 `aggregate` 合，不相乘（相乘等于 AND，会把该给部分分的题压成 0/1）。
- 判分和跑批分开：`harness/score.py` 读已有的运行重判，所以自判两遍、长度偏差、插假事实这些校验不用重跑 agent。

## 重复次数和噪声

- 每个 (题, 配置) 至少 **5 次**。上一轮实测：同题同配置两次运行的分差中位 6.1、平均 7.9，单次标准差约 7 分，而配置之间的效应是 2–3 分——不重复就什么都测不出来。
- 主指标两个一起报：`mean_score`（和外部可比）和 `pass_hat_k = C(c,k)/C(n,k)`（k 次全过的概率，比的是稳不稳）。有效样本不足 k 返回 NaN，不返回 1.0。
- 顺序：同一道题的各配置连着跑（随机区组），种子记进 `results.json`；`--deterministic` 退回"重复在外层、配置在内层"的轮转，和 dsh-dev-bench 对齐。
- 缓存键是 `(run_id, task_id, config_id, attempt)` 四元组。
- 配置之间的差要不要信，看两个对照：提示同义改写、工具故障注入（照 HAL 的 `R_fault = 有故障的准确率 / 基线准确率`）。

## 和 dsh-dev-bench 的字段对应

| 这里 | 那边 | 说明 |
|---|---|---|
| `usage.input_tokens` 等 | `metrics.tokens.{freshInputTokens, cacheReadTokens, outputTokens, reasoningTokens, requestCount}` | 名字按那边写，移过去不用改 |
| `behaviour.n_tool_calls` | `metrics.trajectory.{stepCount, toolCallCount, toolCallsByName}` | 同上 |
| `status` | `status: passed/failed/invalid/prepared` | 一样 |
| `trial_name` | `runId = C<config>R<rep>` | 那边 configId 每维最多 9 档，这里用可读短名 |
| `config_id` | （没有） | 这是这边新增的一层 |
| `pass_hat_k` | （没有，只有 `passRate = passed/(passed+failed)`） | 名字特意区分开 |
