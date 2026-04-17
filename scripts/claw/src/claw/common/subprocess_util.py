"""Windows-safe subprocess runner: resolves .cmd / .bat shims via shutil.which."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any


def which(tool: str) -> str | None:
    return shutil.which(tool)


def require(tool: str) -> str:
    p = shutil.which(tool)
    if not p:
        raise FileNotFoundError(
            f"required external tool `{tool}` not found on PATH. "
            f"Try `claw doctor` for install hints."
        )
    return p


def run(tool: str, *args: str, check: bool = True, **kwargs: Any) -> subprocess.CompletedProcess:
    """Run `tool` with full-path resolution, capturing stdout/stderr by default."""
    bin_path = require(tool)
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    return subprocess.run([bin_path, *args], check=check, **kwargs)


def run_stream(tool: str, *args: str, **kwargs: Any) -> subprocess.Popen:
    """Start `tool` without capturing; caller manages streams."""
    bin_path = require(tool)
    return subprocess.Popen([bin_path, *args], **kwargs)
