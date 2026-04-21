import pytest
from click.testing import CliRunner
from claw.__main__ import cli

@pytest.mark.parametrize("noun", ["doctor", "completion"])
def test_system_help(runner: CliRunner, noun):
    res = runner.invoke(cli, [noun, "--help"])
    assert res.exit_code == 0

def test_doctor_exec(runner: CliRunner):
    res = runner.invoke(cli, ["doctor"])
    assert res.exit_code in (0, 3, 4)

@pytest.mark.parametrize("shell", ["bash", "zsh", "fish", "pwsh"])
def test_completion_exec(runner: CliRunner, shell):
    res = runner.invoke(cli, ["completion", shell])
    assert res.exit_code == 0
