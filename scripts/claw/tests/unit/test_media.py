"""Unit tests for `claw media` (ffmpeg/ffprobe-driven)."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from .._helpers import (
    assert_json_output,
    assert_ok,
    assert_video_duration,
    invoke,
    require_tool,
)

NOUN = "media"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# INSPECT
# ──────────────────────────────────────────────────────────────────────────────

class TestInfo:
    def test_json(self, runner: CliRunner, sample_mp4) -> None:
        require_tool("ffprobe")
        data = assert_json_output(invoke(runner, NOUN, "info", str(sample_mp4()), "--json"))
        assert "streams" in data or "format" in data


# ──────────────────────────────────────────────────────────────────────────────
# TRANSFORM (ffmpeg)
# ──────────────────────────────────────────────────────────────────────────────

class TestTrim:
    def test_basic(self, runner: CliRunner, sample_mp4, tmp_path: Path) -> None:
        require_tool("ffmpeg")
        out = tmp_path / "t.mp4"
        invoke(runner, NOUN, "trim", str(sample_mp4(seconds=3)),
               "--from", "0", "--to", "1", "--out", str(out))
        assert out.exists()


class TestCompress:
    def test_crf(self, runner: CliRunner, sample_mp4, tmp_path: Path) -> None:
        require_tool("ffmpeg")
        out = tmp_path / "c.mp4"
        invoke(runner, NOUN, "compress", str(sample_mp4()),
               "--crf", "28", "--out", str(out))
        assert out.exists()


class TestScale:
    def test_geometry(self, runner: CliRunner, sample_mp4, tmp_path: Path) -> None:
        require_tool("ffmpeg")
        out = tmp_path / "s.mp4"
        invoke(runner, NOUN, "scale", str(sample_mp4()),
               "--geometry", "64x64", "--out", str(out))
        assert out.exists()


class TestSpeed:
    def test_2x(self, runner: CliRunner, sample_mp4, tmp_path: Path) -> None:
        require_tool("ffmpeg")
        out = tmp_path / "sp.mp4"
        invoke(runner, NOUN, "speed", str(sample_mp4(seconds=2)),
               "--factor", "2", "--out", str(out))
        assert out.exists()


class TestFade:
    def test_in_out(self, runner: CliRunner, sample_mp4, tmp_path: Path) -> None:
        require_tool("ffmpeg")
        out = tmp_path / "f.mp4"
        invoke(runner, NOUN, "fade", str(sample_mp4(seconds=2)),
               "--in", "0.5", "--out-sec", "0.5", "--out", str(out))
        assert out.exists()


class TestGif:
    def test_basic(self, runner: CliRunner, sample_mp4, tmp_path: Path) -> None:
        require_tool("ffmpeg")
        out = tmp_path / "g.gif"
        invoke(runner, NOUN, "gif", str(sample_mp4(seconds=2)),
               "--start", "0", "--duration", "1", "--width", "64",
               "--fps", "10", "--out", str(out))
        assert out.exists()


class TestThumbnail:
    def test_at(self, runner: CliRunner, sample_mp4, tmp_path: Path) -> None:
        require_tool("ffmpeg")
        out = tmp_path / "th.png"
        invoke(runner, NOUN, "thumbnail", str(sample_mp4()),
               "--at", "0:00:00.5", "--out", str(out))
        assert out.exists()


class TestExtractAudio:
    def test_mp3(self, runner: CliRunner, sample_mp4, tmp_path: Path) -> None:
        require_tool("ffmpeg")
        out = tmp_path / "a.mp3"
        invoke(runner, NOUN, "extract-audio", str(sample_mp4()),
               "--format", "mp3", "--out", str(out))
        assert out.exists()


class TestConcat:
    def test_two_clips(self, runner: CliRunner, sample_mp4, tmp_path: Path) -> None:
        require_tool("ffmpeg")
        a = sample_mp4(name="a.mp4", seconds=1)
        b = sample_mp4(name="b.mp4", seconds=1)
        out = tmp_path / "c.mp4"
        invoke(runner, NOUN, "concat", str(a), str(b),
               "--reencode", "--out", str(out))
        assert out.exists()


class TestLoudnorm:
    def test_help(self, runner: CliRunner) -> None:
        # Real loudnorm is two-pass, slow — help-coverage covers parseability.
        res = invoke(runner, NOUN, "loudnorm", "--help")
        assert_ok(res)


class TestCropAuto:
    def test_help(self, runner: CliRunner) -> None:
        # Sample fixture is uniform color; cropdetect won't do anything useful.
        res = invoke(runner, NOUN, "crop-auto", "--help")
        assert_ok(res)


class TestBurnSubs:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "burn-subs", "--help")
        assert_ok(res)
