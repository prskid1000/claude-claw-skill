"""Every verb is invokable without a Python traceback.

Catches lazy-import errors and decorator regressions. We don't validate the
*behavior* — invoking with no args should still produce either Click's
"Missing argument" usage or the verb's own help, never an unhandled exception.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from .._discovery import ALL_VERBS
from .._helpers import invoke


def _id(row: tuple[str, str, str | None]) -> str:
    noun, verb, _ = row
    return f"{noun}_{verb}"


@pytest.mark.parametrize("row", ALL_VERBS, ids=[_id(r) for r in ALL_VERBS])
def test_verb_runtime_invocable(
    runner: CliRunner, row: tuple[str, str, str | None]
) -> None:
    noun, verb, skip_reason = row
    if skip_reason is not None:
        # Module import itself failed — typically a missing optional extra.
        # External-tool deps are policy-fail (require_tool), so any module-load
        # failure is a real bug. Surface it.
        raise AssertionError(
            f"verb module for `{noun} {verb}` failed to import: {skip_reason}"
        )

    res = invoke(runner, noun, verb)

    if res.exit_code == 2:
        # Standard Click usage error — "Missing argument" / "Missing option".
        assert "Error:" in res.output or "Usage:" in res.output, (
            f"`{noun} {verb}` exited 2 without standard message:\n{res.output}"
        )
    elif res.exit_code in (0, 1):
        # 0 = ran defaults / showed help; 1 = clean failure (e.g. file not found).
        pass
    else:
        # Anything else (3, 4, ...) is an explicit non-zero exit; allow as long
        # as no traceback was emitted (already asserted by `invoke`).
        pass
