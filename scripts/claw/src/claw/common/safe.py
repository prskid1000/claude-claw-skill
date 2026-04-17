"""Safe-by-default file writes: temp + atomic rename + optional .bak sidecar."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import IO, Callable


def safe_write(path: Path | str, writer: Callable[[IO[bytes]], None], *,
               mode: str = "wb", force: bool = False, backup: bool = False,
               mkdir: bool = False) -> Path:
    """Write to `path` via a temp file in the same directory, then os.replace.

    writer receives an open file object. On any exception the temp file is removed.
    Returns the final Path.
    """
    p = Path(path)
    if p.exists() and not force:
        raise FileExistsError(
            f"{p} exists (pass --force to overwrite, --backup to .bak it first)"
        )
    if mkdir:
        p.parent.mkdir(parents=True, exist_ok=True)
    elif not p.parent.exists():
        raise FileNotFoundError(
            f"parent directory does not exist: {p.parent} (pass --mkdir to create it)"
        )

    if backup and p.exists():
        shutil.copy2(p, p.with_suffix(p.suffix + ".bak"))

    fd, tmp = tempfile.mkstemp(prefix=".claw-", suffix=p.suffix, dir=p.parent)
    try:
        with os.fdopen(fd, mode) as f:
            writer(f)
        os.replace(tmp, p)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return p


def safe_copy(src: Path | str, dst: Path | str, *, force: bool = False,
              backup: bool = False, mkdir: bool = False) -> Path:
    """Copy src → dst with the same safety contract as safe_write."""
    dst_p = Path(dst)
    src_p = Path(src)
    if dst_p.exists() and not force:
        raise FileExistsError(f"{dst_p} exists (pass --force)")
    if mkdir:
        dst_p.parent.mkdir(parents=True, exist_ok=True)
    if backup and dst_p.exists():
        shutil.copy2(dst_p, dst_p.with_suffix(dst_p.suffix + ".bak"))
    shutil.copy2(src_p, dst_p)
    return dst_p
