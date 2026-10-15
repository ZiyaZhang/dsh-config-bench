"""判分：读已经跑完的运行，逐个 scorer 打分，写回 result.json，再汇总成 results.json。

判分不跑 agent、不联网，所以同一批运行可以重判任意多次：改了 scorer 或清单，重跑这个就行。
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import scorers  # noqa: E402
from harness.spec import ROOT, Task, load_tasks  # noqa: E402

PYTEST_LINE = re.compile(r"(\d+) (passed|failed|error|errors)")


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool

    def pytest_counts(self) -> tuple:
        passed = failed = 0
        for n, kind in PYTEST_LINE.findall(self.stdout[-4000:]):
            if kind == "passed":
                passed = int(n)
            else:
                failed += int(n)
        return passed, failed


class Trial:
    """一次运行，判分时看到的就是它留下的目录。"""

    def __init__(self, dir: Path):
        self.dir = dir
        self.result: Dict[str, Any] = json.loads((dir / "result.json").read_text(encoding="utf-8"))

    @property
    def workspace(self) -> Path:
        return self.dir / "workspace"

    def deliverable_path(self, task: Task) -> Optional[Path]:
        d = task.deliverable
        if d.get("kind") == "file":
            return self.workspace / d["name"]
        return None

    def run_in_sandbox(self, command: List[str], timeout_sec: int, copy_in=(), cwd: str = ".") -> SandboxResult:
        """把工作区复制一份，把干净的测试覆盖进去再跑——改过测试的运行占不到便宜。"""
        with tempfile.TemporaryDirectory(prefix="dsh-bench-score-") as tmp:
            work = Path(tmp) / "work"
            shutil.copytree(self.workspace, work, symlinks=True)
            for src, dest in copy_in:
                src = Path(src)
                target = work / dest
                if src.is_dir():
                    shutil.copytree(src, target, dirs_exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, target)
            try:
                p = subprocess.run(command, cwd=work / cwd, capture_output=True, text=True, timeout=timeout_sec)
                return SandboxResult(p.returncode, p.stdout, p.stderr, False)
            except subprocess.TimeoutExpired as e:
                return SandboxResult(-1, (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or ""),
                                     "", True)


    def run_each(self, dirs: List[str], command: List[str], timeout_sec: int, copy_in=()) -> Dict[str, SandboxResult]:
        """一份沙箱里按目录逐个跑：24 道练习各跑各的，互不影响。"""
        out: Dict[str, SandboxResult] = {}
        with tempfile.TemporaryDirectory(prefix="dsh-bench-score-") as tmp:
            work = Path(tmp) / "work"
            shutil.copytree(self.workspace, work, symlinks=True)
            for src, dest in copy_in:
                src = Path(src)
                target = work / dest
                if src.is_dir():
                    shutil.copytree(src, target, dirs_exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, target)
            for d in dirs:
                try:
                    p = subprocess.run(command, cwd=work / d, capture_output=True, text=True, timeout=timeout_sec)
                    out[d] = SandboxResult(p.returncode, p.stdout, p.stderr, False)
                except subprocess.TimeoutExpired:
                    out[d] = SandboxResult(-1, "", "", True)
        return out


def score_trial(trial: Trial, task: Task) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for spec in task.scorers:
        fn = scorers.get(spec["type"])
        s = fn(trial, task, spec)
        out[spec.get("name", spec["type"])] = {"value": s.value, "passed": s.passed,
                                               "reason": s.reason, "detail": s.detail, "source": s.source}
    return out


def aggregate(values: List[Optional[float]], how: str) -> Optional[float]:
    got = [v for v in values if v is not None]
    if not got:
        return None                     # 一条都判不了就是判不了，不是 0 分
    if how == "min":
        return min(got)
    return sum(got) / len(got)


def pass_hat_k(n_pass: int, n: int, k: int) -> Optional[float]:
    """k 次全过的概率；有效次数不足 k 时判不了，返回 None 而不是 1.0。"""
    if n < k:
        return None
    return math.comb(n_pass, k) / math.comb(n, k) if n_pass >= k else 0.0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="harness.score", description="给一批运行判分并汇总")
    ap.add_argument("run_id")
    ap.add_argument("--k", type=int, default=2, help="pass^k 的 k")
    a = ap.parse_args(argv)

    base = ROOT / "runs" / a.run_id
    if not base.exists():
        raise SystemExit(f"没有这一批：{base}")
    tasks = {t.task_id: t for t in load_tasks()}
    rows: List[Dict[str, Any]] = []
    for res in sorted(base.glob("*/*/result.json")):
        trial = Trial(res.parent)
        task = tasks[trial.result["task_id"]]
        if trial.result.get("status") == "invalid":
            scored: Dict[str, Any] = {}
            value = None
        else:
            scored = score_trial(trial, task)
            value = aggregate([v["value"] for v in scored.values()], task.raw.get("aggregate", "mean"))
        trial.result["scorer_results"] = scored
        trial.result["score"] = value
        trial.result["resolved"] = all(v.get("passed") for v in scored.values()) if scored and all(
            v.get("passed") is not None for v in scored.values()) else None
        res.write_text(json.dumps(trial.result, ensure_ascii=False, indent=2), encoding="utf-8")
        rows.append(trial.result)
        why = ", ".join("%s=%s" % (k, v["reason"]) for k, v in scored.items()) or trial.result.get("failure_mode", "")
        print("%s: %s  (%s)" % (trial.result["trial_name"], value if value is not None else "判不了", why))

    per_config: Dict[str, Any] = {}
    for r in rows:
        c = per_config.setdefault(r["config_id"], {
            "n_planned": 0, "n_valid": 0, "n_resolved": 0, "resolved_ids": [], "unresolved_ids": [],
            "excluded_ids": [], "scores": []})
        c["n_planned"] += 1
        if r.get("status") == "invalid":
            c["excluded_ids"].append(r["trial_name"])
            continue
        c["n_valid"] += 1
        if r.get("score") is not None:
            c["scores"].append(r["score"])
        if r.get("resolved"):
            c["n_resolved"] += 1
            c["resolved_ids"].append(r["trial_name"])
        else:
            c["unresolved_ids"].append(r["trial_name"])
    for c in per_config.values():
        c["mean_score"] = (sum(c["scores"]) / len(c["scores"])) if c["scores"] else None
        c["pass_hat_k"] = pass_hat_k(c["n_resolved"], c["n_valid"], a.k)
        c.pop("scores")

    meta_path = base / "run_metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    out = {"run_id": a.run_id, "k": a.k, "config": meta, "per_config": per_config}
    (base / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n汇总写到", base / "results.json")
    for cid, c in per_config.items():
        print(f"  {cid:8s} 有效 {c['n_valid']}/{c['n_planned']}  平均分 "
              f"{c['mean_score'] if c['mean_score'] is not None else '判不了'}  pass^{a.k} {c['pass_hat_k']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
