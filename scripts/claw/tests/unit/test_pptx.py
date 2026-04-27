"""Unit tests for `claw pptx`."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from .._helpers import (
    assert_json_output,
    assert_ok,
    assert_pptx_slides,
    invoke,
)

NOUN = "pptx"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────────────────────────────────────

class TestNew:
    def test_minimum(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.pptx"
        invoke(runner, NOUN, "new", str(out))
        assert out.exists()


class TestAddSlide:
    def test_with_title(self, runner: CliRunner, sample_pptx) -> None:
        p = sample_pptx()
        invoke(runner, NOUN, "add-slide", str(p),
               "--title", "Hello", "--force")
        assert_pptx_slides(p, 2)

    def test_with_body_and_notes(self, runner: CliRunner, sample_pptx) -> None:
        invoke(runner, NOUN, "add-slide", str(sample_pptx()),
               "--title", "T", "--body", "- one\n- two",
               "--notes", "speaker note", "--force")


class TestFromOutline:
    def test_basic(self, runner: CliRunner, tmp_path: Path) -> None:
        md = tmp_path / "outline.md"
        md.write_text("# Title\n\n## Slide A\n\n- bullet\n\n## Slide B\n\nbody\n",
                       encoding="utf-8")
        out = tmp_path / "deck.pptx"
        invoke(runner, NOUN, "from-outline", str(out), "--data", str(md))
        assert out.exists()
        assert_pptx_slides(out, 3)


# ──────────────────────────────────────────────────────────────────────────────
# INSERT OBJECTS
# ──────────────────────────────────────────────────────────────────────────────

class TestAddTable:
    def test_csv(self, runner: CliRunner, sample_pptx, sample_csv) -> None:
        invoke(runner, NOUN, "add-table", str(sample_pptx()),
               "--slide", "1", "--data", str(sample_csv()), "--header", "--force")


class TestAddChart:
    def test_bar(self, runner: CliRunner, sample_pptx, sample_csv) -> None:
        invoke(runner, NOUN, "add-chart", str(sample_pptx()),
               "--slide", "1", "--type", "bar",
               "--data", str(sample_csv()), "--title", "T", "--force")


class TestAddImage:
    def test_basic(self, runner: CliRunner, sample_pptx, sample_png) -> None:
        invoke(runner, NOUN, "add-image", str(sample_pptx()),
               "--slide", "1", "--image", str(sample_png()),
               "--at", "C", "--force")


class TestAddShape:
    def test_rect(self, runner: CliRunner, sample_pptx) -> None:
        invoke(runner, NOUN, "add-shape", str(sample_pptx()),
               "--slide", "1", "--kind", "rect",
               "--at", "1in,1in", "--size", "2in,1in",
               "--text", "Hi", "--fill", "#3366CC", "--force")


class TestFill:
    def test_help(self, runner: CliRunner) -> None:
        # `fill` requires a placeholder/shape that exists on the layout — fragile
        # to test without a known-template. Help-coverage validates parseability.
        res = invoke(runner, NOUN, "fill", "--help")
        assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# ADVANCED
# ──────────────────────────────────────────────────────────────────────────────

class TestBrand:
    def test_accent_color(self, runner: CliRunner, sample_pptx) -> None:
        invoke(runner, NOUN, "brand", str(sample_pptx()),
               "--accent-color", "1F4E78", "--force")


class TestChart:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "chart", "--help")
        assert_ok(res)
        assert "refresh" in res.output


class TestNotes:
    def test_set(self, runner: CliRunner, sample_pptx) -> None:
        invoke(runner, NOUN, "notes", str(sample_pptx()),
               "--slide", "1", "--text", "presenter note", "--force")

    def test_clear(self, runner: CliRunner, sample_pptx) -> None:
        p = sample_pptx()
        invoke(runner, NOUN, "notes", str(p), "--slide", "1", "--text", "x", "--force")
        invoke(runner, NOUN, "notes", str(p), "--slide", "1", "--clear", "--force")


class TestReorder:
    def test_basic(self, runner: CliRunner, sample_pptx) -> None:
        p = sample_pptx(slides=3)
        invoke(runner, NOUN, "reorder", str(p), "--order", "3,1,2", "--force")


class TestImage:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "image", "--help")
        assert_ok(res)


class TestLink:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "link", "--help")
        assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# META
# ──────────────────────────────────────────────────────────────────────────────

class TestMeta:
    def test_get(self, runner: CliRunner, sample_pptx) -> None:
        data = assert_json_output(
            invoke(runner, NOUN, "meta", "get", str(sample_pptx()), "--json")
        )
        assert isinstance(data, dict)

    def test_set(self, runner: CliRunner, sample_pptx) -> None:
        p = sample_pptx()
        invoke(runner, NOUN, "meta", "set", str(p), "--title", "MyDeck", "--force")
        data = assert_json_output(invoke(runner, NOUN, "meta", "get", str(p), "--json"))
        assert data.get("title") == "MyDeck"
