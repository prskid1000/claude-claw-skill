import pytest
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli

NOUN = "pptx"

def test_pptx_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0

def test_pptx_new(runner: CliRunner, tmp_path: Path):
    pytest.importorskip("pptx")
    out = tmp_path / "new.pptx"
    res = runner.invoke(cli, [NOUN, "new", str(out)])
    assert res.exit_code == 0
    assert out.exists()

def test_pptx_add_slide(runner: CliRunner, sample_pptx):
    p = sample_pptx()
    res = runner.invoke(cli, [NOUN, "add-slide", str(p), "--title", "Hello", "--force"])
    assert res.exit_code == 0

def test_pptx_add_table(runner: CliRunner, sample_pptx, sample_csv):
    p = sample_pptx()
    csv_p = sample_csv()
    res = runner.invoke(cli, [NOUN, "add-table", str(p), "--slide", "1", "--data", str(csv_p), "--force"])
    assert res.exit_code == 0
