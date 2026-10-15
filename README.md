# dsh-config-bench

比 harness 配置的评测集：**模型固定，比的是 DSH 怎么配**——subagent 的深度上限和同时存活上限、工具集、模式、插件。每道题在每个配置下各跑几次，报质量、花费、时长和一组行为计数。

起因是一轮 5,073 次运行的 subagent 上限评测（[subagent-limits-eval](https://github.com/ZiyaZhang/subagent-limits-eval)）：那轮的题、跑批、判分和行为统计都是一次性搭的，这个仓库把能复用的部分固定下来。

## 现状

- 5 道自研题（2 道办公报告配事实清单、24 道 Python 练习、16 步串行链、61 文件的工具包），题面和工作区都在仓库里。
- 7 个配置（不开 subagent、D1×K1/K4/K8、D2K8、D3K64、告知上限的对照），一文件一配置。
- 3 个确定性 scorer（事实清单、隐藏测试、逐项精确匹配），接口见 `scorers/__init__.py`。

还没做完的见 `docs/TODO.md`：判分用的完整测试和答案键还在开发机上，跑批程序正在从上一轮的脚本移过来。

## 目录

| 目录 | 内容 |
|---|---|
| `tasks/<task_id>/` | 一题一目录：`task.yaml`、`prompt.md`、`workspace/`、`expected/`（金标、清单、文件清单） |
| `adapters/<suite>/` | 公开评测集的适配器：把外部题转成和自研题同样形状的 `tasks/` 目录，题本身不进仓库 |
| `configs/<config_id>.yaml` | 被比的配置，一文件一个 |
| `scorers/` | 判分，一个 type 一个文件 |
| `harness/` | 跑批、从会话日志算指标、判分校验、行为标注 |
| `runs/<run_id>/` | 运行结果；单次运行的 `result.json` 是唯一事实来源，顶层 `results.json` 随时可以重建 |
| `docs/design.md` | 字段、schema、重复次数和噪声的规定，以及和 `dsh-dev-bench` 的对应关系 |

## 记分

- scorer 判不了返回 `value=None`，不返回 0；指标缺了就留空，不回退成别的量。
- 基础设施故障的运行记成 `invalid`，id 单列，不进分母。
- 每个（题，配置）至少跑 5 次：上一轮实测同题同配置两次运行的分差中位 6.1、单次标准差约 7 分，而配置之间的差是 2–3 分。
