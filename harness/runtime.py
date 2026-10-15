"""把一份固定版本的 DSH 装进 .runtime/，每次跑批用同一份，和桌面端那份互不影响。"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .spec import ROOT

RUNTIME = ROOT / ".runtime"
DEFAULT_VERSION = "0.2.0-rc.2"


def dsh_bin(version: str = DEFAULT_VERSION) -> Path:
    bin_js = RUNTIME / "node_modules" / "@deepseek-ai" / "dsh" / "lib" / "bin.js"
    if bin_js.exists() and installed_version() == version:
        return bin_js
    install(version)
    if not bin_js.exists():
        raise SystemExit(f"装完了却找不到 {bin_js}")
    return bin_js


def installed_version() -> str | None:
    pkg = RUNTIME / "node_modules" / "@deepseek-ai" / "dsh" / "package.json"
    if not pkg.exists():
        return None
    return json.loads(pkg.read_text(encoding="utf-8")).get("version")


def install(version: str = DEFAULT_VERSION) -> None:
    RUNTIME.mkdir(exist_ok=True)
    (RUNTIME / "package.json").write_text(
        json.dumps({"name": "dsh-config-bench-runtime", "private": True,
                    "dependencies": {"@deepseek-ai/dsh": version}}, indent=2) + "\n", encoding="utf-8")
    print(f"装 @deepseek-ai/dsh@{version} 到 {RUNTIME} …")
    r = subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=RUNTIME,
                       capture_output=True, text=True, env={**os.environ, "npm_config_loglevel": "error"})
    if r.returncode != 0:
        raise SystemExit("npm install 失败：\n" + (r.stderr or r.stdout)[-2000:])
    print("装好了：", installed_version())
