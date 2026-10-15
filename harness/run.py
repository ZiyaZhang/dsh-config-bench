"""跑批：题 × 配置 × 重复。

一次运行一个目录，目录里是这次运行的全部东西：工作区、给 DSH 的补丁、事件流、result.json。
顺序默认随机区组——同一道题的各配置连着跑，块内随机，种子记进 results.json；
--deterministic 退回"重复在外层、配置在内层"的轮转，和 dsh-dev-bench 对齐。
"""
from __future__ import annotations

import json
import os
import random
import re
import shutil
import subprocess
import tarfile
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import env as envmod
from .runtime import dsh_bin
from .spec import ROOT, Config, Task, fragment, load_configs, load_tasks

DSH_ERROR = re.compile(r"^dsh: ([A-Z0-9_]+):", re.M)
INFRA = {"EMPTY_RESPONSE", "RATE_LIMIT", "SERVER", "TIMEOUT", "TRANSPORT"}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Trial:
    task: Task
    config: Config
    attempt: int
    n_attempts: int
    run_id: str

    @property
    def name(self) -> str:
        return f"{self.task.task_id}.{self.config.config_id}.{self.attempt}-of-{self.n_attempts}.{self.run_id}"

    @property
    def dir(self) -> Path:
        return ROOT / "runs" / self.run_id / self.task.task_id / self.name


def plan(tasks: List[Task], configs: List[Config], attempts: int, seed: int,
         run_id: str, deterministic: bool = False) -> List[Trial]:
    trials = [Trial(t, c, a, attempts, run_id)
              for t in tasks for c in configs for a in range(1, attempts + 1)]
    if deterministic:
        trials.sort(key=lambda x: (x.attempt, x.task.task_id, x.config.config_id))
        return trials
    rng = random.Random(seed)
    out: List[Trial] = []
    for t in tasks:                                   # 一道题的所有格子连着跑
        block = [x for x in trials if x.task.task_id == t.task_id]
        rng.shuffle(block)
        out.extend(block)
    return out


def materialise(trial: Trial) -> Path:
    ws = trial.dir / "workspace"
    ws.mkdir(parents=True, exist_ok=True)
    spec = trial.task.workspace
    kind = spec.get("kind", "empty")
    if kind == "empty":
        return ws
    if kind == "tar":
        src = trial.task.dir / spec["path"]
        with tarfile.open(src) as tf:
            tf.extractall(ws, filter="data")
        return ws
    raise SystemExit(f"还不支持的工作区类型：{kind}")


def patches_for(trial: Trial, ep: envmod.Endpoint) -> List[Path]:
    cfg = trial.dir / "patches"
    cfg.mkdir(parents=True, exist_ok=True)
    out = []
    base = fragment("base", {"MODEL": ep.model,
                            "EFFORT_LINE": (f"    reasoningEffort: {ep.effort}" if ep.effort else "    # 没设推理强度"), "MAX_TOKENS": str(ep.max_tokens), "THINKING": ep.thinking})
    out.append(_w(cfg / "00-base.yml", base))
    if trial.task.web:
        out.append(_w(cfg / "10-web.yml", fragment("web", {"SEARCH_BASE_URL": ep.search_base_url or ""})))
    else:
        out.append(_w(cfg / "10-noweb.yml", fragment("noweb", {})))
    out.append(_w(cfg / f"20-{trial.config.config_id}.yml", trial.config.patch_text))
    return out


def dsh_home(run_id: str) -> Path:
    """一个批次共用一份 DSH home（profile 和装好的插件在里面），工作区和补丁仍按运行分开。"""
    home = ROOT / "runs" / run_id / "dsh-home"
    home.mkdir(parents=True, exist_ok=True)
    return home


def _w(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def deliverable_ok(trial: Trial) -> Optional[bool]:
    d = trial.task.deliverable
    ws = trial.dir / "workspace"
    if d.get("kind") == "file":
        f = ws / d["name"]
        if not f.exists():
            return False
        return f.stat().st_size >= int(d.get("min_bytes", 0))
    if d.get("kind") == "changed_files":
        return None          # 交付是"改了哪些文件"，由判分去看，不在这里判
    return None


def run_one(trial: Trial, ep: envmod.Endpoint, bin_js: Path, dry: bool = False) -> Dict[str, Any]:
    ws = materialise(trial)
    patches = patches_for(trial, ep)
    argv = ["node", str(bin_js), "--profile", "headless"]
    for p in patches:
        argv += ["--patch", str(p)]
    argv += ["--json", "-"]          # 题面从 stdin 进去
    rec: Dict[str, Any] = {
        "run_id": trial.run_id, "task_id": trial.task.task_id, "task_version": trial.task.version,
        "config_id": trial.config.config_id, "attempt": trial.attempt, "trial_name": trial.name,
        "endpoint": ep.redacted(), "dsh_version": bin_js.parents[1].name and _pkg_version(bin_js),
        "agent_timeout_sec": trial.task.agent_timeout_sec,
        "trial_started_at": now(),
    }
    if dry:
        rec.update(status="prepared", failure_mode="none", agent_started_at=None, agent_ended_at=None)
        (trial.dir / "result.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        return rec

    events = trial.dir / "events.jsonl"
    stderr = trial.dir / "stderr.log"
    rec["agent_started_at"] = now()
    t0 = time.time()
    timed_out = False
    with open(events, "wb") as fo, open(stderr, "wb") as fe:
        proc = subprocess.Popen(argv, cwd=ws, stdin=subprocess.PIPE, stdout=fo, stderr=fe,
                                env={**os.environ, **ep.child_env(trial.task.web),
                                     "DSH_HOME": str(dsh_home(trial.run_id))})
        try:
            proc.communicate(trial.task.prompt.encode("utf-8"), timeout=trial.task.agent_timeout_sec)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            proc.communicate()
    rec["agent_ended_at"] = now()
    rec["agent_duration_sec"] = round(time.time() - t0, 1)
    rec["exit_code"] = proc.returncode
    err = stderr.read_text(encoding="utf-8", errors="replace")[-20000:]
    codes = set(DSH_ERROR.findall(err))
    infra = sorted(codes & INFRA)
    ok = deliverable_ok(trial)
    if timed_out:
        rec.update(status="failed", failure_mode="agent_timeout")
    elif infra:
        rec.update(status="invalid", failure_mode=infra[0].lower())
    elif proc.returncode != 0:
        rec.update(status="failed", failure_mode="nonzero_exit")
    elif ok is False:
        rec.update(status="failed", failure_mode="no_deliverable")
    else:
        rec.update(status="passed", failure_mode="none")
    rec["dsh_error_codes"] = sorted(codes)
    (trial.dir / "result.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return rec


def _pkg_version(bin_js: Path) -> str:
    pkg = bin_js.parents[1] / "package.json"
    return json.loads(pkg.read_text(encoding="utf-8")).get("version", "?") if pkg.exists() else "?"


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="harness.run", description="跑一批：题 × 配置 × 重复")
    ap.add_argument("--tasks", help="逗号分隔的 task_id；不给就是全部")
    ap.add_argument("--configs", help="逗号分隔的 config_id；不给就是全部")
    ap.add_argument("--attempts", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--run-id")
    ap.add_argument("--deterministic", action="store_true", help="退回确定性轮转顺序")
    ap.add_argument("--plan-only", action="store_true", help="只打印顺序，不跑，不要密钥")
    ap.add_argument("--dry", action="store_true", help="建目录、物化工作区、生成补丁，但不启动 DSH")
    a = ap.parse_args(argv)

    tasks = load_tasks(a.tasks.split(",") if a.tasks else None)
    configs = load_configs(a.configs.split(",") if a.configs else None)
    if not tasks or not configs:
        raise SystemExit("没有选到题或配置")
    run_id = a.run_id or f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    trials = plan(tasks, configs, a.attempts, a.seed, run_id, a.deterministic)

    print(f"run_id {run_id}：{len(tasks)} 题 × {len(configs)} 配置 × {a.attempts} 次 = {len(trials)} 次运行")
    for i, t in enumerate(trials, 1):
        print(f"  {i:3d}  {t.task.task_id:18s} {t.config.config_id:8s} 第 {t.attempt} 次")
    if a.plan_only:
        return 0

    ep = envmod.load()
    bin_js = dsh_bin()
    meta = {"run_id": run_id, "started_at": now(), "tasks": [t.task_id for t in tasks],
            "configs": [c.config_id for c in configs], "n_attempts": a.attempts,
            "seed": a.seed, "order": "deterministic" if a.deterministic else "randomised-block",
            "endpoint": ep.redacted(), "dsh_version": _pkg_version(bin_js)}
    out = ROOT / "runs" / run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "run_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    for i, t in enumerate(trials, 1):
        print(f"[{i}/{len(trials)}] {t.name} …", flush=True)
        rec = run_one(t, ep, bin_js, dry=a.dry)
        print(f"      {rec['status']} / {rec['failure_mode']}"
              + (f" / {rec.get('agent_duration_sec')}s" if rec.get("agent_duration_sec") else ""), flush=True)
    meta["ended_at"] = now()
    (out / "run_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("结果在", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
