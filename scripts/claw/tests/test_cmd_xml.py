import pytest
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli

NOUN = "xml"

def test_xml_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0

def test_xml_xpath(runner: CliRunner, sample_xml):
    pytest.importorskip("lxml")
    p = sample_xml()
    res = runner.invoke(cli, [NOUN, "xpath", str(p), "//a/text()"])
    assert res.exit_code == 0
    assert "1" in res.output

def test_xml_fmt(runner: CliRunner, sample_xml, tmp_path: Path):
    pytest.importorskip("lxml")
    p = sample_xml()
    out = tmp_path / "fmt.xml"
    res = runner.invoke(cli, [NOUN, "fmt", str(p), "--out", str(out)])
    assert res.exit_code == 0
