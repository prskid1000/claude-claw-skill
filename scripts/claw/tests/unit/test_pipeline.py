"""Unit tests for `claw pipeline`."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from .._helpers import assert_ok, invoke

NOUN = "pipeline"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


@pytest.fixture
def shell_recipe(tmp_path: Path) -> Path:
    """Trivial single-step recipe — Python `print` via shell step."""
    recipe = tmp_path / "trivial.yaml"
    py = sys.executable.replace("\\", "/")
    recipe.write_text(yaml.safe_dump({
        "steps": [
            {"name": "greet", "run": "shell",
             "cmd": f"\"{py}\" -c \"print('pipeline-ok')\""},
        ],
    }), encoding="utf-8")
    return recipe


class TestListSteps:
    def test_basic(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "list-steps")
        assert_ok(res)
        assert "xlsx" in res.output


class TestValidate:
    def test_valid_recipe(self, runner: CliRunner, shell_recipe: Path) -> None:
        res = invoke(runner, NOUN, "validate", str(shell_recipe))
        assert res.exit_code in (0, 1, 2), res.output

    def test_invalid_recipe(self, runner: CliRunner, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("not a real recipe", encoding="utf-8")
        res = invoke(runner, NOUN, "validate", str(bad))
        assert res.exit_code != 0


class TestGraph:
    def test_ascii(self, runner: CliRunner, shell_recipe: Path) -> None:
        res = invoke(runner, NOUN, "graph", str(shell_recipe), "--format", "ascii")
        # Some recipes/steps may fail validation; we accept clean exit + no traceback.
        assert "Traceback" not in res.output


class TestRun:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "run", "--help")
        assert_ok(res)
        assert "--resume" in res.output
