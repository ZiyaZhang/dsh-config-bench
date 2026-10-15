"""逐项精确匹配：交付文件里按行给出的答案和金标比。

金标是 {"1": "1048", "2": "1098", ...}；交付文件里每行形如 "1: 1048"。
用在串行链这种每步只有一个正确整数的题上。
"""
from __future__ import annotations

import json
import re

from . import Score, scorer

_LINE = re.compile(r"^\s*(\d+)\s*[:：.]\s*(-?\d+)\s*$", re.M)


@scorer("exact_answers")
def score_exact_answers(trial, task, spec) -> Score:
    doc = trial.deliverable_path(task)
    if doc is None or not doc.exists():
        return Score(value=None, passed=None, reason="没有交付文件，判不了")
    key_path = task.dir / spec["path"]
    if spec.get("assets") == "pending" or not key_path.exists():
        return Score(value=None, passed=None, reason=f"答案还没放进来（{spec[path]}）")
    key = json.loads(key_path.read_text(encoding="utf-8"))
    got = dict(_LINE.findall(doc.read_text(encoding="utf-8", errors="replace")))
    right = [k for k, v in key.items() if got.get(str(k)) == str(v)]
    return Score(
        value=len(right) / len(key),
        passed=len(right) == len(key),
        reason=f"对 {len(right)}/{len(key)} 步",
        detail={"right_steps": right, "answered": len(got)},
    )
