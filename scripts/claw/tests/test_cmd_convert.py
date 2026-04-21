import pytest
import json
import sys
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli
from .conftest import skip_without

NOUN = "convert"

def test_convert_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0

def test_convert_list_formats(runner: CliRunner):
    skip_without("pandoc")
    res = runner.invoke(cli, [NOUN, "list-formats", "--json"])
    assert res.exit_code == 0
    data = json.loads(res.output)
    # The output is a dict with 'input' and 'output' lists
    assert "html" in data["output"] or "html" in data["input"]

@pytest.mark.xfail(sys.platform == "win32", reason="Windows file locking issues in CI")
def test_convert_md2pdf_nolatex(runner: CliRunner, sample_md, tmp_path: Path):
    skip_without("pandoc")
    pytest.importorskip("fitz")
    md = sample_md()
    out = tmp_path / "out.pdf"
    # SRC DST are positional
    res = runner.invoke(cli, [NOUN, "md2pdf-nolatex", str(md), str(out)])
    assert res.exit_code == 0
    assert out.exists()

def test_convert_convert(runner: CliRunner, sample_md, tmp_path: Path):
    skip_without("pandoc")
    md = sample_md()
    out = tmp_path / "out.html"
    res = runner.invoke(cli, [NOUN, "convert", str(md), str(out)])
    assert res.exit_code == 0
    assert out.exists()
