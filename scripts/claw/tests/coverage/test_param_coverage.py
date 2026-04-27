"""Every flag on every verb is parseable.

Catches:
  * decorator typos that prevent a flag from registering
  * conflicting short-options across the same verb
  * dangling required/eager option default-callbacks
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from .._discovery import FLAG_PARAMS
from .._helpers import invoke


def _id(row: tuple[str, str, str, object]) -> str:
    noun, verb, flag, _ = row
    return f"{noun}_{verb}__{flag.lstrip('-').replace('-', '_')}"


@pytest.mark.parametrize("row", FLAG_PARAMS, ids=[_id(r) for r in FLAG_PARAMS])
def test_flag_listed_in_verb_help(
    runner: CliRunner, row: tuple[str, str, str, object]
) -> None:
    """Every option declared on the click.Command must appear in --help."""
    noun, verb, flag, skip_reason = row
    if skip_reason is not None:
        raise AssertionError(
            f"verb {noun} {verb} failed to load: {skip_reason}"
        )
    if flag == "<load-failure>":
        raise AssertionError(f"verb {noun} {verb} did not yield params")

    res = invoke(runner, noun, verb, "--help")
    assert res.exit_code == 0, f"`claw {noun} {verb} --help` failed:\n{res.output}"
    assert flag in res.output, (
        f"flag {flag!r} not visible in `{noun} {verb} --help`:\n{res.output}"
    )
