"""Exit codes + structured error emission."""

from __future__ import annotations

import json
import sys


EXIT_OK = 0
EXIT_GENERIC = 1
EXIT_USAGE = 2
EXIT_PARTIAL = 3
EXIT_INPUT = 4
EXIT_SYSTEM = 5
EXIT_INTERRUPT = 130


def emit_error(msg: str, *, code: int = EXIT_GENERIC, hint: str | None = None,
               doc_url: str | None = None, as_json: bool = False) -> None:
    if as_json:
        payload = {"error": msg, "code": code}
        if hint:
            payload["hint"] = hint
        if doc_url:
            payload["doc_url"] = doc_url
        sys.stderr.write(json.dumps(payload) + "\n")
    else:
        sys.stderr.write(f"error: {msg}\n")
        if hint:
            sys.stderr.write(f"hint: {hint}\n")
        if doc_url:
            sys.stderr.write(f"docs: {doc_url}\n")


def die(msg: str, *, code: int = EXIT_GENERIC, hint: str | None = None,
        doc_url: str | None = None, as_json: bool = False) -> None:
    emit_error(msg, code=code, hint=hint, doc_url=doc_url, as_json=as_json)
    sys.exit(code)
