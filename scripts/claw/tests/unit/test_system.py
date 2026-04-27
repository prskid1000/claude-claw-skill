"""Unit tests for `claw doctor` and `claw completion`."""

from __future__ import annotations

from click.testing import CliRunner

from .._helpers import assert_ok, invoke


def test_doctor_help(runner: CliRunner) -> None:
    assert_ok(invoke(runner, "doctor", "--help"))


def test_doctor_packages_scope(runner: CliRunner) -> None:
    res = invoke(runner, "doctor", "--scope", "packages")
    # 0 = all ok, 3 = warnings, 4 = failures — all acceptable, but no traceback.
    assert res.exit_code in (0, 3, 4), res.output


def test_doctor_json(runner: CliRunner) -> None:
    res = invoke(runner, "doctor", "--scope", "packages", "--json")
    assert "Traceback" not in res.output


def test_completion_help(runner: CliRunner) -> None:
    assert_ok(invoke(runner, "completion", "--help"))


def test_completion_bash(runner: CliRunner) -> None:
    res = invoke(runner, "completion", "bash")
    assert_ok(res)
    assert "_claw_completion" in res.output or "complete" in res.output


def test_completion_zsh(runner: CliRunner) -> None:
    res = invoke(runner, "completion", "zsh")
    assert_ok(res)


def test_completion_fish(runner: CliRunner) -> None:
    res = invoke(runner, "completion", "fish")
    assert_ok(res)


def test_completion_pwsh(runner: CliRunner) -> None:
    res = invoke(runner, "completion", "pwsh")
    assert_ok(res)
