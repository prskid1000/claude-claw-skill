import pytest
from click.testing import CliRunner
from claw.__main__ import cli

# doc, sheet, email
@pytest.mark.parametrize("noun", ["doc", "sheet", "email"])
def test_gws_help(runner: CliRunner, noun):
    res = runner.invoke(cli, [noun, "--help"])
    assert res.exit_code == 0

@pytest.mark.parametrize("verb", ["send", "draft"])
def test_email_dry_run(runner: CliRunner, verb):
    res = runner.invoke(cli, ["email", verb, "--to", "x@y.z", "--subject", "s", "--body", "b", "--dry-run"])
    assert res.exit_code == 0
