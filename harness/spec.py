"""读 tasks/*/task.yaml 和 configs/*.yaml。

只认仓库里的目录约定：tasks/<task_id>/task.yaml 的 task_id 必须和目录名一致，
configs/<config_id>.yaml 同理；下划线开头的配置文件是公共片段，不是被比的配置。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent


def _load_yaml(path: Path) -> Any:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:  # 没装 pyyaml 时用一个够用的子集解析器
        return _mini_yaml(path.read_text(encoding="utf-8"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _scalar(s: str) -> Any:
    s = s.strip()
    if s.startswith(("'", '"')) and s.endswith(("'", '"')) and len(s) >= 2:
        return s[1:-1]
    if s in ("true", "false"):
        return s == "true"
    if s == "null" or s == "":
        return None
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        return [_scalar(x) for x in _split_top(inner)] if inner else []
    if s.startswith("{") and s.endswith("}"):
        out: Dict[str, Any] = {}
        inner = s[1:-1].strip()
        for part in _split_top(inner):
            if not part.strip():
                continue
            k, _, v = part.partition(":")
            out[k.strip()] = _scalar(v)
        return out
    return s


def _split_top(s: str) -> List[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def _mini_yaml(text: str) -> Any:
    """只支持本仓库 task.yaml / config.yaml 用到的写法：顶层 key: value、块标量、列表项。"""
    root: Dict[str, Any] = {}
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  ") or raw.startswith("- "):
            continue  # 顶层解析器只收顶层条目；嵌套块下面单独处理
        key, _, rest = raw.partition(":")
        key, rest = key.strip(), rest.strip()
        if rest in ("|", "|-", ">"):
            body = []
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                body.append(lines[i][2:] if lines[i].startswith("  ") else "")
                i += 1
            root[key] = "\n".join(body).rstrip()
        elif rest == "":
            block, start = [], i
            while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("- ") or not lines[i].strip()):
                block.append(lines[i])
                i += 1
            root[key] = _mini_block(block) if block else None
            if not block:
                i = start
        else:
            root[key] = _scalar(rest)
    return root


def _mini_block(block: List[str]) -> Any:
    items = [b for b in block if b.strip()]
    if items and items[0].lstrip().startswith("- "):
        return [_scalar(b.lstrip()[2:]) for b in items]
    out: Dict[str, Any] = {}
    for b in items:
        k, _, v = b.strip().partition(":")
        out[k.strip()] = _scalar(v)
    return out


@dataclass
class Task:
    task_id: str
    dir: Path
    raw: Dict[str, Any]

    @property
    def version(self) -> int: return int(self.raw.get("version", 1))
    @property
    def web(self) -> bool: return bool(self.raw.get("web", False))
    @property
    def prompt(self) -> str: return (self.dir / "prompt.md").read_text(encoding="utf-8")
    @property
    def workspace(self) -> Dict[str, Any]: return self.raw.get("workspace") or {"kind": "empty"}
    @property
    def deliverable(self) -> Dict[str, Any]: return self.raw.get("deliverable") or {}
    @property
    def agent_timeout_sec(self) -> int: return int(self.raw.get("max_agent_timeout_sec", 3600))
    @property
    def max_test_timeout_sec(self) -> int: return int(self.raw.get("max_test_timeout_sec", 900))
    @property
    def scorers(self) -> List[Dict[str, Any]]: return list(self.raw.get("scorers") or [])


@dataclass
class Config:
    config_id: str
    path: Path
    raw: Dict[str, Any]
    patch_text: str

    @property
    def is_default(self) -> bool: return bool(self.raw.get("default", False))
    @property
    def title(self) -> str: return str(self.raw.get("title", self.config_id))


def load_tasks(only: Optional[List[str]] = None) -> List[Task]:
    out = []
    for d in sorted((ROOT / "tasks").iterdir()):
        f = d / "task.yaml"
        if not f.exists():
            continue
        raw = _load_yaml(f)
        if raw.get("task_id") != d.name:
            raise ValueError(f"{f}: task_id {raw.get('task_id')!r} 和目录名 {d.name!r} 不一致")
        if only and d.name not in only:
            continue
        out.append(Task(d.name, d, raw))
    return out


def load_configs(only: Optional[List[str]] = None) -> List[Config]:
    out = []
    for f in sorted((ROOT / "configs").glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        raw = _load_yaml(f)
        if raw.get("config_id") != f.stem:
            raise ValueError(f"{f}: config_id {raw.get('config_id')!r} 和文件名 {f.stem!r} 不一致")
        if only and f.stem not in only:
            continue
        text = f.read_text(encoding="utf-8")
        patch = text.split("patch:", 1)[1] if "patch:" in text else ""
        patch = "\n".join(line[2:] if line.startswith("  ") else line for line in patch.split("\n"))
        out.append(Config(f.stem, f, raw, patch.strip() + "\n"))
    return out


def fragment(name: str, subs: Dict[str, str]) -> str:
    text = (ROOT / "configs" / f"_{name}.yaml").read_text(encoding="utf-8")
    for k, v in subs.items():
        text = text.replace("{{%s}}" % k, v)
    left = re.findall(r"\{\{(\w+)\}\}", text)
    if left:
        raise ValueError(f"_{name}.yaml 里还有没替换的占位符：{sorted(set(left))}")
    return text
