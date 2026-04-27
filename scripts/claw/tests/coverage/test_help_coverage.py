"""Every noun and every verb shows --help cleanly.

Mechanical, parametric. Catches regressions where a verb registration is
broken (lazy import error) or a noun loses a verb without notice.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from claw.__main__ import NOUNS
from .._discovery import NOUN_VERB_PAIRS
from .._helpers import assert_ok, invoke


# ──────────────────────────────────────────────────────────────────────────────
# top-level
# ──────────────────────────────────────────────────────────────────────────────

def test_top_level_help(runner: CliRunner) -> None:
    res = invoke(runner, "--help")
    assert_ok(res)
    assert "Usage:" in res.output
    # Every noun must appear in the top-level help.
    for noun in NOUNS:
        assert noun in res.output, f"noun {noun!r} missing from top-level help"


# ──────────────────────────────────────────────────────────────────────────────
# every noun
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("noun", sorted(NOUNS.keys()))
def test_noun_help(runner: CliRunner, noun: str) -> None:
    res = invoke(runner, noun, "--help")
    assert_ok(res)
    assert "Usage:" in res.output


# ──────────────────────────────────────────────────────────────────────────────
# every verb
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "noun,verb",
    NOUN_VERB_PAIRS,
    ids=[f"{n}_{v}" for n, v in NOUN_VERB_PAIRS],
)
def test_verb_help(runner: CliRunner, noun: str, verb: str) -> None:
    res = invoke(runner, noun, verb, "--help")
    assert_ok(res)
    assert "Usage:" in res.output


# ──────────────────────────────────────────────────────────────────────────────
# `claw help <command>` alias
# ──────────────────────────────────────────────────────────────────────────────

def test_help_alias_no_args(runner: CliRunner) -> None:
    res = invoke(runner, "help")
    assert_ok(res)
    assert "Usage:" in res.output


def test_help_alias_for_noun(runner: CliRunner) -> None:
    res = invoke(runner, "help", "xlsx")
    assert_ok(res)
    assert "Usage:" in res.output


def test_help_alias_for_verb(runner: CliRunner) -> None:
    res = invoke(runner, "help", "xlsx", "new")
    assert_ok(res)
    assert "Usage:" in res.output


def test_help_alias_for_unknown_command_exits_nonzero(runner: CliRunner) -> None:
    res = invoke(runner, "help", "no-such-thing")
    assert res.exit_code != 0
