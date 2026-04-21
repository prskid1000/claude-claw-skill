import pytest
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli

NOUN = "img"

def test_img_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0

def test_img_resize(runner: CliRunner, sample_png, tmp_path: Path):
    p = sample_png()
    out = tmp_path / "resized.png"
    res = runner.invoke(cli, [NOUN, "resize", str(p), "--geometry", "50x50", "--out", str(out)])
    assert res.exit_code == 0
    assert out.exists()

def test_img_fit(runner: CliRunner, sample_png, tmp_path: Path):
    p = sample_png()
    out = tmp_path / "fit.png"
    res = runner.invoke(cli, [NOUN, "fit", str(p), "--size", "64x64", "--out", str(out)])
    assert res.exit_code == 0

def test_img_convert(runner: CliRunner, sample_png, tmp_path: Path):
    p = sample_png()
    out = tmp_path / "out.webp"
    res = runner.invoke(cli, [NOUN, "convert", str(p), str(out)])
    assert res.exit_code == 0

def test_img_exif(runner: CliRunner, sample_png, tmp_path: Path):
    p = sample_png()
    res = runner.invoke(cli, [NOUN, "exif", str(p), "--json"])
    assert res.exit_code in (0, 2)

def test_img_watermark(runner: CliRunner, sample_png, tmp_path: Path):
    p = sample_png()
    out = tmp_path / "wm.png"
    res = runner.invoke(cli, [NOUN, "watermark", str(p), "--text", "DRAFT", "--out", str(out)])
    assert res.exit_code == 0
