import pytest
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli
from .conftest import skip_without

NOUN = "docx"

def test_docx_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0
    assert "Usage:" in res.output

def test_docx_new(runner: CliRunner, tmp_path: Path):
    pytest.importorskip("docx")
    out = tmp_path / "new.docx"
    res = runner.invoke(cli, [NOUN, "new", str(out)])
    assert res.exit_code == 0
    assert out.exists()

def test_docx_read(runner: CliRunner, sample_docx):
    p = sample_docx()
    res = runner.invoke(cli, [NOUN, "read", str(p), "--text"])
    assert res.exit_code == 0
    assert "Title" in res.output

def test_docx_add_heading(runner: CliRunner, sample_docx):
    p = sample_docx()
    res = runner.invoke(cli, [NOUN, "add-heading", str(p), "--text", "Subheading", "--level", "2", "--force"])
    assert res.exit_code == 0

def test_docx_add_paragraph(runner: CliRunner, sample_docx):
    p = sample_docx()
    res = runner.invoke(cli, [NOUN, "add-paragraph", str(p), "--text", "new content", "--bold", "--force"])
    assert res.exit_code == 0

def test_docx_add_table(runner: CliRunner, sample_docx, sample_csv):
    p = sample_docx()
    csv_p = sample_csv()
    res = runner.invoke(cli, [NOUN, "add-table", str(p), "--data", str(csv_p), "--header", "--force"])
    assert res.exit_code == 0

def test_docx_add_image(runner: CliRunner, sample_docx, sample_png):
    p = sample_docx()
    img = sample_png()
    res = runner.invoke(cli, [NOUN, "add-image", str(p), "--image", str(img), "--width", "2.0", "--force"])
    assert res.exit_code == 0

def test_docx_header_footer(runner: CliRunner, sample_docx):
    p = sample_docx()
    res1 = runner.invoke(cli, [NOUN, "header", str(p), "--text", "HEADER", "--force"])
    assert res1.exit_code == 0
    res2 = runner.invoke(cli, [NOUN, "footer", str(p), "--text", "FOOTER", "--force"])
    assert res2.exit_code == 0

def test_docx_toc(runner: CliRunner, sample_docx):
    p = sample_docx()
    res = runner.invoke(cli, [NOUN, "toc", str(p), "--force"])
    assert res.exit_code == 0

def test_docx_meta(runner: CliRunner, sample_docx):
    p = sample_docx()
    res = runner.invoke(cli, [NOUN, "meta", "get", str(p)])
    assert res.exit_code == 0

def test_docx_insert(runner: CliRunner, sample_docx):
    p = sample_docx()
    # Needs --before or --after
    res = runner.invoke(cli, [NOUN, "insert", "pagebreak", str(p), "--before", "Title", "--force"])
    assert res.exit_code == 0

def test_docx_style(runner: CliRunner, sample_docx):
    p = sample_docx()
    # Needs --to or --all-matching-style
    res = runner.invoke(cli, [NOUN, "style", "apply", str(p), "--name", "Normal", "--all-matching-style", "Normal", "--force"])
    assert res.exit_code == 0

def test_docx_from_md(runner: CliRunner, sample_md, tmp_path: Path):
    pytest.importorskip("docx")
    skip_without("pandoc")
    md = sample_md()
    out = tmp_path / "from-md.docx"
    res = runner.invoke(cli, [NOUN, "from-md", str(out), "--data", str(md)])
    assert res.exit_code == 0
    assert out.exists()
