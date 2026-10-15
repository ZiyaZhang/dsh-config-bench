"""事实清单判分：交付的文档里写对了清单上的多少条。

清单是一个 JSON 列表，每条：
  {"id": "visa-14d", "fact": "中国护照免签 30 天", "accept": ["30 天", "30天"],
   "reject": ["15 天"], "weight": 1}
accept 里任意一条出现即算写对；reject 命中算写错（单列，不扣分）。
匹配只做规范化后的子串比对，不调模型——同一份报告判多少次结果都一样。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import Score, scorer

_WS = re.compile(r"[\s,，、]+")


def _norm(s: str) -> str:
    return _WS.sub("", s).lower()


@scorer("checklist")
def score_checklist(trial, task, spec) -> Score:
    doc = trial.deliverable_path(task)
    if doc is None or not doc.exists():
        return Score(value=None, passed=None, reason="没有交付文件，判不了")
    text = _norm(doc.read_text(encoding="utf-8", errors="replace"))
    items = json.loads((task.dir / spec["path"]).read_text(encoding="utf-8"))
    right = wrong = 0.0
    total = 0.0
    hits, misses, wrongs = [], [], []
    for it in items:
        w = float(it.get("weight", 1))
        total += w
        if any(_norm(a) in text for a in it.get("accept", [])):
            right += w
            hits.append(it["id"])
        else:
            misses.append(it["id"])
        if any(_norm(r) in text for r in it.get("reject", [])):
            wrong += w
            wrongs.append(it["id"])
    if total == 0:
        return Score(value=None, reason="清单是空的")
    return Score(
        value=right / total,
        reason=f"写对 {right:g}/{total:g} 条，写错 {wrong:g} 条",
        detail={"right": right, "total": total, "wrong": wrong,
                "hit_ids": hits, "missed_ids": misses, "wrong_ids": wrongs},
    )
