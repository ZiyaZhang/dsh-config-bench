"""判分用的 Python：装在 .runtime/venv 里，和本机的 Python 环境分开，版本固定。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .spec import ROOT

VENV = ROOT / ".runtime" / "venv"
PYTEST_VERSION = "8.3.4"


def python() -> str:
    exe = VENV / "bin" / "python"
    if not exe.exists():
        print(f"建判分用的虚拟环境 {VENV} …")
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    if not (VENV / "bin" / "pytest").exists():
        print(f"装 pytest=={PYTEST_VERSION} …")
        subprocess.run([str(exe), "-m", "pip", "install", "-q", f"pytest=={PYTEST_VERSION}"], check=True)
    return str(exe)
