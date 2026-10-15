"""模型端点和密钥：只从环境变量或 macOS 钥匙串读，进程内用完就算，不落盘、不打印。

要设的变量（内网地址和密钥都不进仓库）：
  DSH_BENCH_BASE_URL    模型端点
  DSH_BENCH_MODEL       模型名（默认 deepseek-flash）
  DSH_BENCH_EFFORT      推理强度（默认 max）
  DSH_BENCH_API_KEY     模型密钥；没设就按 DSH_BENCH_KEYCHAIN（service[:account]）去钥匙串取
  DSH_BENCH_SEARCH_BASE_URL / DSH_BENCH_SEARCH_API_KEY   联网题才要
  DSH_BENCH_DIRECT=1    端点所在主机不走本机代理（内网端点 + 本机挂代理时要开）
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Dict, Optional


def _keychain(spec: str) -> Optional[str]:
    service, _, account = spec.partition(":")
    cmd = ["security", "find-generic-password", "-s", service, "-w"]
    if account:
        cmd[2:2] = ["-a", account]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except Exception:
        return None
    return out.stdout.strip() or None


@dataclass
class Endpoint:
    base_url: str
    model: str
    effort: str
    api_key: str
    max_tokens: int = 256000
    thinking: str = "enabled"
    direct: bool = False
    search_base_url: Optional[str] = None
    search_api_key: Optional[str] = None

    def child_env(self, web: bool) -> Dict[str, str]:
        env = {"DEEPSEEK_BASE_URL": self.base_url, "DEEPSEEK_API_KEY": self.api_key,
               "NODE_USE_SYSTEM_CA": "1"}
        if self.direct:
            # 端点在内网、本机又挂着代理时：这个主机不走代理。
            host = self.base_url.split("//")[-1].split("/")[0].split(":")[0]
            env.update({"NO_PROXY": host, "no_proxy": host,
                        "HTTP_PROXY": "", "HTTPS_PROXY": "", "http_proxy": "", "https_proxy": ""})
        if web:
            if not (self.search_base_url and self.search_api_key):
                raise SystemExit("这道题要联网，但 DSH_BENCH_SEARCH_BASE_URL / DSH_BENCH_SEARCH_API_KEY 没设")
            env["SEARCH_API_KEY"] = self.search_api_key
        return env

    def redacted(self) -> Dict[str, str]:
        """能写进 result.json 的部分：有没有密钥，没有密钥本身。"""
        return {"base_url_host": self.base_url.split("//")[-1].split("/")[0],
                "model": self.model, "effort": self.effort, "max_tokens": self.max_tokens, "thinking": self.thinking,
                "api_key": "set" if self.api_key else "missing"}


def load() -> Endpoint:
    key = os.environ.get("DSH_BENCH_API_KEY", "")
    if not key and os.environ.get("DSH_BENCH_KEYCHAIN"):
        key = _keychain(os.environ["DSH_BENCH_KEYCHAIN"]) or ""
        if key:
            key = os.environ.get("DSH_BENCH_KEY_PREFIX", "") + key
    base = os.environ.get("DSH_BENCH_BASE_URL", "")
    if not base or not key:
        raise SystemExit("没有端点或密钥：先设 DSH_BENCH_BASE_URL，以及 DSH_BENCH_API_KEY 或 DSH_BENCH_KEYCHAIN")
    skey = os.environ.get("DSH_BENCH_SEARCH_API_KEY", "")
    if not skey and os.environ.get("DSH_BENCH_SEARCH_KEYCHAIN"):
        skey = _keychain(os.environ["DSH_BENCH_SEARCH_KEYCHAIN"]) or ""
    return Endpoint(base_url=base,
                    model=os.environ.get("DSH_BENCH_MODEL", "deepseek-flash"),
                    effort=os.environ.get("DSH_BENCH_EFFORT", "max"),
                    api_key=key,
                    max_tokens=int(os.environ.get("DSH_BENCH_MAX_TOKENS", "256000")),
                    thinking=os.environ.get("DSH_BENCH_THINKING", "enabled"),
                    direct=os.environ.get("DSH_BENCH_DIRECT", "") not in ("", "0", "false"),
                    search_base_url=os.environ.get("DSH_BENCH_SEARCH_BASE_URL") or None,
                    search_api_key=skey or None)
