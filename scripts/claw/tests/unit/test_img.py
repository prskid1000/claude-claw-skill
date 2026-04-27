"""Unit tests for `claw img`."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from .._helpers import (
    assert_image_dims,
    assert_image_format,
    assert_json_output,
    assert_ok,
    invoke,
)

NOUN = "img"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# RESIZE / FIT / THUMB / CROP / PAD
# ──────────────────────────────────────────────────────────────────────────────

class TestResize:
    def test_geometry_pixels(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "r.png"
        invoke(runner, NOUN, "resize", str(sample_png()),
               "--geometry", "50x50!", "--out", str(out))
        assert_image_dims(out, 50, 50)


class TestFit:
    def test_size(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "f.png"
        invoke(runner, NOUN, "fit", str(sample_png()),
               "--size", "60x60", "--out", str(out))
        assert_image_dims(out, 60, 60)


class TestThumb:
    def test_max_edge(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "t.png"
        invoke(runner, NOUN, "thumb", str(sample_png(size=(200, 100))),
               "--max", "50", "--out", str(out))
        assert out.exists()


class TestCrop:
    def test_box(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "c.png"
        invoke(runner, NOUN, "crop", str(sample_png()),
               "--box", "10,10,40,40", "--out", str(out))
        assert_image_dims(out, 40, 40)


class TestPad:
    def test_letterbox(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "p.png"
        invoke(runner, NOUN, "pad", str(sample_png()),
               "--size", "200x200", "--color", "#000000", "--out", str(out))
        assert_image_dims(out, 200, 200)


# ──────────────────────────────────────────────────────────────────────────────
# CONVERT / FORMAT
# ──────────────────────────────────────────────────────────────────────────────

class TestConvert:
    def test_to_jpeg(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "c.jpg"
        invoke(runner, NOUN, "convert", str(sample_png()), str(out))
        assert_image_format(out, "JPEG")


class TestToWebp:
    def test_basic(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "w.webp"
        invoke(runner, NOUN, "to-webp", str(sample_png()), "--out", str(out))
        assert_image_format(out, "WEBP")


class TestToJpeg:
    def test_basic(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "j.jpg"
        invoke(runner, NOUN, "to-jpeg", str(sample_png()),
               "--bg", "white", "--quality", "80", "--out", str(out))
        assert_image_format(out, "JPEG")


# ──────────────────────────────────────────────────────────────────────────────
# ENHANCE / SHARPEN
# ──────────────────────────────────────────────────────────────────────────────

class TestEnhance:
    def test_autocontrast(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "e.png"
        invoke(runner, NOUN, "enhance", str(sample_png()),
               "--autocontrast", "--out", str(out))
        assert out.exists()


class TestSharpen:
    def test_unsharp(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "s.png"
        invoke(runner, NOUN, "sharpen", str(sample_png()),
               "--radius", "2", "--amount", "150", "--out", str(out))
        assert out.exists()


# ──────────────────────────────────────────────────────────────────────────────
# EXIF / WATERMARK / COMPOSITE / OVERLAY
# ──────────────────────────────────────────────────────────────────────────────

class TestExif:
    def test_read(self, runner: CliRunner, sample_jpg) -> None:
        # Basic Pillow-saved JPEG has no EXIF — verb should still exit cleanly.
        res = invoke(runner, NOUN, "exif", str(sample_jpg()), "--json")
        assert_ok(res)

    def test_strip(self, runner: CliRunner, sample_jpg, tmp_path: Path) -> None:
        out = tmp_path / "ns.jpg"
        invoke(runner, NOUN, "exif", str(sample_jpg()),
               "--strip", "--out", str(out))
        assert out.exists()


class TestWatermark:
    def test_text(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "w.png"
        invoke(runner, NOUN, "watermark", str(sample_png()),
               "--text", "draft", "--position", "BR", "--out", str(out))
        assert out.exists()


class TestComposite:
    def test_basic(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        bg = sample_png(name="bg.png", size=(200, 200), color=(0, 0, 0))
        fg = sample_png(name="fg.png", size=(50, 50), color=(255, 0, 0))
        out = tmp_path / "comp.png"
        invoke(runner, NOUN, "composite",
               "--bg", str(bg), "--fg", str(fg),
               "--at", "10,10", "--out", str(out))
        assert out.exists()


class TestOverlay:
    def test_corner(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        bg = sample_png(name="bg.png", size=(200, 200), color=(255, 255, 255))
        logo = sample_png(name="logo.png", size=(40, 40), color=(0, 0, 255))
        out = tmp_path / "over.png"
        invoke(runner, NOUN, "overlay", str(bg),
               "--logo", str(logo), "--position", "BR", "--out", str(out))
        assert out.exists()


# ──────────────────────────────────────────────────────────────────────────────
# RENAME / BATCH / GIF-FROM-FRAMES
# ──────────────────────────────────────────────────────────────────────────────

class TestRename:
    def test_help(self, runner: CliRunner) -> None:
        # Real test would mutate fixture filenames; help-coverage covers parse.
        res = invoke(runner, NOUN, "rename", "--help")
        assert_ok(res)


class TestBatch:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "batch", "--help")
        assert_ok(res)


class TestGifFromFrames:
    def test_basic(self, runner: CliRunner, sample_png, tmp_path: Path) -> None:
        frames = tmp_path / "frames"
        frames.mkdir()
        for i in range(3):
            sample_png(name=f"frames/f{i:02}.png", color=(i * 80, 0, 0))
        out = tmp_path / "anim.gif"
        invoke(runner, NOUN, "gif-from-frames", str(frames),
               "--fps", "10", "--out", str(out))
        assert out.exists()
