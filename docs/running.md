# 怎么跑

## 一次性准备

```sh
python3 -m harness.run --plan-only          # 只打印顺序，不需要密钥
```
第一次真跑会自动把固定版本的 DSH 装进 `.runtime/`（`@deepseek-ai/dsh@0.2.0-rc.2`，和桌面端那份互不影响）。

## 端点和密钥

都从环境变量读，内网地址和密钥不进仓库：

| 变量 | 说明 |
|---|---|
| `DSH_BENCH_BASE_URL` | 模型端点 |
| `DSH_BENCH_MODEL` / `DSH_BENCH_EFFORT` | 模型名；推理强度留空就不发这个字段 |
| `DSH_BENCH_MAX_TOKENS` / `DSH_BENCH_THINKING` | 一次回复的上限、思考开关（默认 256000 / enabled） |
| `DSH_BENCH_API_KEY` | 密钥；也可以用 `DSH_BENCH_KEYCHAIN=service[:account]` 从 macOS 钥匙串取，再用 `DSH_BENCH_KEY_PREFIX` 拼前缀 |
| `DSH_BENCH_SEARCH_BASE_URL` / `DSH_BENCH_SEARCH_API_KEY` | 联网题才要 |

密钥只在进程内传给 DSH，不写进任何文件；`result.json` 里只记端点主机名和"有没有密钥"。

## 跑

```sh
python3 -m harness.run --tasks chain-16 --configs d0,d1k8 --attempts 5 --seed 1
```

- 顺序默认随机区组：同一道题的各配置连着跑，种子记进 `run_metadata.json`；`--deterministic` 退回轮转顺序。
- `--dry` 建目录、物化工作区、生成补丁但不启动 DSH，用来检查配置。
- 结果在 `runs/<run_id>/<task_id>/<trial_name>/`：`workspace/`、`patches/`、`events.jsonl`、`stderr.log`、`result.json`。

## 换端点时会撞到的三件事

实测记录，省得再查一遍：

- `sandbox-policy` 只认 `read-only` / `workspace-write` / `danger-full-access`，用 `DSH_PERMISSION_MODE=auto` 会让八个插件起不来。
- 一次回复的上限默认 256000，端点低于这个数就报 `INVALID_REQUEST`，用 `DSH_BENCH_MAX_TOKENS` 调小。
- 思考和推理强度不是所有端点都收：Anthropic 兼容端点要求思考带预算，用 `DSH_BENCH_THINKING=disabled`；不支持 `reasoningEffort` 的把 `DSH_BENCH_EFFORT` 留空。
