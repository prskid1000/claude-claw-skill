"""Windows-safe `gws` CLI invoker.

The `gws` CLI installs as a `.cmd` shim on Windows; `subprocess.run` in list
form can't execute `.cmd` without a shell, and `shell=True` breaks when the
JSON payload contains `|`, `&`, `>`, or `<` — those get interpreted by cmd.exe.

Workaround: resolve the shim to its JS entry point and invoke `node run-gws.js`
directly. List-form subprocess, no shell.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


_CACHED_NODE_ARGS: list[str] | None = None


def _resolve_node_args() -> list[str]:
    """Return `[node, run-gws.js]` argv prefix; raise if gws isn't installed."""
    global _CACHED_NODE_ARGS
    if _CACHED_NODE_ARGS is not None:
        return list(_CACHED_NODE_ARGS)

    gws = shutil.which("gws")
    if not gws:
        raise FileNotFoundError(
            "required external tool `gws` not found on PATH. "
            "Install: npm install -g @googleworkspace/cli. "
            "Then `gws auth login` to grant scopes."
        )

    node = shutil.which("node")
    if not node:
        raise FileNotFoundError(
            "`node` not on PATH; `gws` requires Node.js. Install Node 18+."
        )

    gws_path = Path(gws).resolve()
    candidates = [
        gws_path.parent / "node_modules" / "@googleworkspace" / "cli" / "run-gws.js",
    ]
    env = os.environ.get("CLAW_GWS_JS")
    if env:
        candidates.insert(0, Path(env))

    for c in candidates:
        if c.exists():
            _CACHED_NODE_ARGS = [node, str(c)]
            return list(_CACHED_NODE_ARGS)

    # Fallback: use the .cmd via shell=False fails on Windows; prefer .cmd with shell=True.
    _CACHED_NODE_ARGS = [gws]
    return list(_CACHED_NODE_ARGS)


def gws_run(*args: str, check: bool = True, **kwargs: Any) -> subprocess.CompletedProcess:
    """Run `gws <args...>` safely on Windows (no shell, no .cmd pitfall)."""
    argv = _resolve_node_args() + list(args)
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("encoding", "utf-8")
    return subprocess.run(argv, check=check, **kwargs)
