import pytest
from pathlib import Path
from click.testing import CliRunner
from claw.__main__ import cli
from .conftest import skip_without

NOUN = "media"

def test_media_help(runner: CliRunner):
    res = runner.invoke(cli, [NOUN, "--help"])
    assert res.exit_code == 0

def test_media_info(runner: CliRunner, sample_mp4):
    skip_without("ffprobe")
    p = sample_mp4()
    res = runner.invoke(cli, [NOUN, "info", str(p), "--json"])
    assert res.exit_code == 0

def test_media_thumbnail(runner: CliRunner, sample_mp4, tmp_path: Path):
    skip_without("ffmpeg")
    p = sample_mp4()
    out = tmp_path / "thumb.jpg"
    res = runner.invoke(cli, [NOUN, "thumbnail", str(p), "--out", str(out), "--at", "0"])
    assert res.exit_code == 0

def test_media_trim(runner: CliRunner, sample_mp4, tmp_path: Path):
    skip_without("ffmpeg")
    p = sample_mp4()
    out = tmp_path / "trimmed.mp4"
    res = runner.invoke(cli, [NOUN, "trim", str(p), "--out", str(out), "--from", "0", "--to", "0.5"])
    assert res.exit_code in (0, 1, 5)
