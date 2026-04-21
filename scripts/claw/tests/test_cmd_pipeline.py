import pytest
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli

NOUN = "pipeline"

def test_pipeline_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0

def test_pipeline_list_steps(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "list-steps"])
    assert res.exit_code == 0
    assert "shell" in res.output
