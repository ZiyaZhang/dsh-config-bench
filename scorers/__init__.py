"""判分接口。

一个 scorer 是一个函数：score(trial, task, spec) -> Score。
注册靠 @scorer("<type>")，task.yaml 里 scorers[].type 对上哪个就用哪个。

规矩（两条，别绕过去）：
  * 判不了就返回 value=None，不要返回 0——缺值和零分是两回事。
  * scorer 自己不跑 agent、不碰网络；它只读这次运行留下的文件和日志，
    所以同一批运行可以离线重判任意多次（harness/score.py）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

REGISTRY: Dict[str, Callable] = {}


@dataclass
class Score:
    value: Optional[float]                      # 0–1；None = 判不了
    passed: Optional[bool] = None               # 布尔主判，没有就留空
    reason: str = ""                            # 一句话，为什么是这个分
    detail: Dict[str, Any] = field(default_factory=dict)
    source: str = "script"                      # script | model_label | human


def scorer(type_name: str):
    def deco(fn: Callable) -> Callable:
        if type_name in REGISTRY:
            raise ValueError(f"scorer type {type_name!r} 已经注册过")
        REGISTRY[type_name] = fn
        fn.scorer_type = type_name
        return fn
    return deco


def get(type_name: str) -> Callable:
    if type_name not in REGISTRY:
        raise KeyError(f"没有这种 scorer: {type_name!r}；已注册：{sorted(REGISTRY)}")
    return REGISTRY[type_name]


from . import checklist, exact_answers, hidden_tests  # noqa: E402,F401  注册用
