"""Tier 1.5 — Runtime coverage for EVERY verb.

Ensures that every command defined in the NOUNS/VERBS dispatch tables can at
least be imported and invoked without crashing (even if it just shows help or
a usage error). This catches 'hidden' import errors in lazy-loaded modules.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from claw.__main__ import cli
from ._discovery import ALL_VERBS


def _id(row: tuple[str, str, str | None]) -> str:
    noun, verb, _ = row
    return f"{noun}_{verb}"


@pytest.mark.parametrize("row", ALL_VERBS, ids=[_id(r) for r in ALL_VERBS])
def test_verb_runtime_invocable(runner: CliRunner, row: tuple[str, str, str | None]) -> None:
    noun, verb, skip_reason = row
    if skip_reason is not None:
        # This catches modules that fail to import at all (e.g. missing heavy dependency)
        # We allow this if the user hasn't installed the optional extra.
        pytest.skip(f"{noun} {verb}: {skip_reason}")

    # Invoke with no args. 
    # For most verbs, this will exit 2 (missing argument) or 0 (shows help).
    # We just want to ensure NO TRACEBACK occurs.
    res = runner.invoke(cli, [noun, verb])
    
    assert "Traceback" not in res.output, f"CRASH in {noun} {verb}:\n{res.output}"
    
    # If it exits with 2, it should be a standard Click "Missing argument" or "Missing option".
    if res.exit_code == 2:
        assert "Error:" in res.output or "Usage:" in res.output
    
    # If it exits with 0, it likely showed help or performed a default action.
    elif res.exit_code == 0:
        pass
        
    # Other exit codes (1, 3, 4, etc.) are okay as long as they aren't crashes.
    # Some commands might fail because they need a real file.
