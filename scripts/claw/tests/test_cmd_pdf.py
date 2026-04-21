import pytest
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli
from .conftest import skip_without

NOUN = "pdf"

def test_pdf_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0
    assert "Usage:" in res.output

def test_pdf_info(runner: CliRunner, sample_pdf):
    pytest.importorskip("fitz")
    p = sample_pdf()
    res = runner.invoke(cli, [NOUN, "info", str(p), "--json"])
    assert res.exit_code == 0

def test_pdf_extract_text(runner: CliRunner, sample_pdf):
    pytest.importorskip("fitz")
    p = sample_pdf()
    res = runner.invoke(cli, [NOUN, "extract-text", str(p)])
    assert res.exit_code == 0
    assert "Page 1" in res.output

def test_pdf_extract_tables(runner: CliRunner, sample_pdf):
    pytest.importorskip("pdfplumber")
    p = sample_pdf()
    res = runner.invoke(cli, [NOUN, "extract-tables", str(p)])
    assert res.exit_code in (0, 3) # 3 if no tables found

def test_pdf_render(runner: CliRunner, sample_pdf, tmp_path: Path):
    pytest.importorskip("fitz")
    p = sample_pdf()
    out = tmp_path / "page1.png"
    res = runner.invoke(cli, [NOUN, "render", str(p), "--page", "1", "-o", str(out)])
    assert res.exit_code == 0
    assert out.exists()

def test_pdf_merge(runner: CliRunner, sample_pdf, tmp_path: Path):
    pytest.importorskip("pypdf")
    p1 = sample_pdf(name="p1.pdf")
    p2 = sample_pdf(name="p2.pdf")
    out = tmp_path / "merged.pdf"
    res = runner.invoke(cli, [NOUN, "merge", str(p1), str(p2), "-o", str(out)])
    assert res.exit_code == 0
    assert out.exists()

def test_pdf_split(runner: CliRunner, sample_pdf, tmp_path: Path):
    pytest.importorskip("pypdf")
    p = sample_pdf()
    outdir = tmp_path / "split"
    outdir.mkdir()
    res = runner.invoke(cli, [NOUN, "split", str(p), "--per-page", "--out-dir", str(outdir)])
    assert res.exit_code == 0

def test_pdf_rotate(runner: CliRunner, sample_pdf, tmp_path: Path):
    pytest.importorskip("pypdf")
    p = sample_pdf()
    out = tmp_path / "rot.pdf"
    res = runner.invoke(cli, [NOUN, "rotate", str(p), "--by", "180", "-o", str(out)])
    assert res.exit_code == 0

def test_pdf_watermark(runner: CliRunner, sample_pdf, tmp_path: Path):
    pytest.importorskip("fitz")
    p = sample_pdf()
    out = tmp_path / "wm.pdf"
    res = runner.invoke(cli, [NOUN, "watermark", str(p), "--text", "CONFIDENTIAL", "-o", str(out)])
    assert res.exit_code == 0

def test_pdf_encrypt_decrypt(runner: CliRunner, sample_pdf, tmp_path: Path):
    pytest.importorskip("pypdf")
    p = sample_pdf()
    enc = tmp_path / "enc.pdf"
    dec = tmp_path / "dec.pdf"
    res1 = runner.invoke(cli, [NOUN, "encrypt", str(p), "--password", "secret", "-o", str(enc)])
    assert res1.exit_code == 0
    res2 = runner.invoke(cli, [NOUN, "decrypt", str(enc), "--password", "secret", "-o", str(dec)])
    assert res2.exit_code == 0

def test_pdf_qr(runner: CliRunner, tmp_path: Path):
    pytest.importorskip("qrcode")
    pytest.importorskip("reportlab")
    out = tmp_path / "qr.pdf"
    res = runner.invoke(cli, [NOUN, "qr", "--value", "https://google.com", "-o", str(out)])
    assert res.exit_code == 0
    assert out.exists()

def test_pdf_barcode(runner: CliRunner, tmp_path: Path):
    pytest.importorskip("reportlab")
    out = tmp_path / "bc.pdf"
    res = runner.invoke(cli, [NOUN, "barcode", "--type", "code128", "--value", "12345", "-o", str(out)])
    assert res.exit_code == 0

def test_pdf_search(runner: CliRunner, sample_pdf):
    pytest.importorskip("fitz")
    p = sample_pdf()
    res = runner.invoke(cli, [NOUN, "search", str(p), "--term", "hello", "--json"])
    assert res.exit_code == 0
