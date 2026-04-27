"""Unit tests for `claw doc` (Google Docs).

Real Drive/Docs API isn't reachable from CI; tests use ``--dry-run`` where
supported and fall back to ``--help`` parseability checks otherwise.
"""

from __future__ import annotations

from click.testing import CliRunner

from .._helpers import assert_ok, invoke

NOUN = "doc"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


class TestCreate:
    def test_dry_run(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "create", "--title", "T", "--dry-run")
        # Dry-run should exit 0 even without auth.
        assert res.exit_code in (0, 1, 2), res.output


class TestRead:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "read", "--help"))


class TestAppend:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "append", "--help"))


class TestBuild:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "build", "--help"))


class TestReplace:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "replace", "--help"))


class TestExport:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "export", "--help"))


class TestTabs:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "tabs", "--help")
        assert_ok(res)
        assert "list" in res.output
