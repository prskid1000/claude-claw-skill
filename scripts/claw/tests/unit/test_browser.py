"""Unit tests for `claw browser` — help/verify only (no headed launches)."""

from __future__ import annotations

from click.testing import CliRunner

from .._helpers import assert_ok, invoke

NOUN = "browser"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


class TestLaunch:
    def test_help(self, runner: CliRunner) -> None:
        # Real launch is interactive; help-coverage validates parseability.
        res = invoke(runner, NOUN, "launch", "--help")
        assert_ok(res)
        assert "--user-data-dir" in res.output


class TestStop:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "stop", "--help"))


class TestVerify:
    def test_no_browser_running(self, runner: CliRunner) -> None:
        # When no debug-port is open, verify exits non-zero with a clean message.
        res = invoke(runner, NOUN, "verify")
        assert "Traceback" not in res.output
