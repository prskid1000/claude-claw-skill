import pytest
from click.testing import CliRunner
from claw.__main__ import cli

NOUN = "browser"

def test_browser_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0
