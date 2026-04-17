"""Stdin/stdout and CSV/JSON helpers for --data / - conventions."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Iterable


def read_text(src: str | Path) -> str:
    if str(src) in ("-", ""):
        return sys.stdin.read()
    return Path(src).read_text(encoding="utf-8")


def read_bytes(src: str | Path) -> bytes:
    if str(src) in ("-", ""):
        return sys.stdin.buffer.read()
    return Path(src).read_bytes()


def read_rows(src: str | Path, *, header: bool = True) -> list[dict[str, Any]] | list[list[Any]]:
    """Detect CSV vs JSON by extension (or .json content) and return rows."""
    text = read_text(src)
    path_str = str(src)
    if path_str.endswith(".json") or text.lstrip().startswith(("[", "{")):
        data = json.loads(text)
        if isinstance(data, dict):
            data = [data]
        return data
    rows = list(csv.reader(text.splitlines()))
    if header and rows:
        cols = rows[0]
        return [dict(zip(cols, r)) for r in rows[1:]]
    return rows


def write_text(dst: str | Path, content: str) -> None:
    if str(dst) in ("-", ""):
        sys.stdout.write(content)
        return
    Path(dst).write_text(content, encoding="utf-8")


def write_rows_csv(dst: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    if not rows:
        write_text(dst, "")
        return
    headers = list(rows[0].keys())
    if str(dst) in ("-", ""):
        w = csv.DictWriter(sys.stdout, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
        return
    with Path(dst).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)


def emit_json(obj: Any) -> None:
    """--json output helper — NDJSON on stdout, one line per record or a single JSON object."""
    sys.stdout.write(json.dumps(obj, default=str, ensure_ascii=False) + "\n")
