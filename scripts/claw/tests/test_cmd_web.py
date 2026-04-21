import pytest
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli

NOUN = "web"

def test_web_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0

def test_web_extract_local(runner: CliRunner, sample_html):
    pytest.importorskip("trafilatura")
    p = sample_html(body="<article><h1>Title</h1><p>content</p></article>")
    res = runner.invoke(cli, [NOUN, "extract", str(p)])
    assert res.exit_code == 0
    assert "content" in res.output
