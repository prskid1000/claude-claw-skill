import pytest
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli

NOUN = "html"

def test_html_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0

def test_html_select(runner: CliRunner, sample_html):
    pytest.importorskip("bs4")
    p = sample_html()
    res = runner.invoke(cli, [NOUN, "select", str(p), "--css", "h1", "--text"])
    assert res.exit_code == 0
    assert "T" in res.output

def test_html_fmt(runner: CliRunner, sample_html, tmp_path: Path):
    pytest.importorskip("bs4")
    p = sample_html()
    out = tmp_path / "fmt.html"
    res = runner.invoke(cli, [NOUN, "fmt", str(p), "--out", str(out)])
    assert res.exit_code == 0

def test_html_strip(runner: CliRunner, sample_html, tmp_path: Path):
    pytest.importorskip("bs4")
    p = sample_html(body="<h1>T</h1><script>alert(1)</script>")
    out = tmp_path / "stripped.html"
    res = runner.invoke(cli, [NOUN, "strip", str(p), "--css", "script", "--out", str(out)])
    assert res.exit_code == 0
