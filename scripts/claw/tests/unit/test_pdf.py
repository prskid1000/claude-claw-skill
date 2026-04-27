"""Unit tests for `claw pdf` (35 verbs)."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from .._helpers import (
    assert_json_output,
    assert_ok,
    assert_pdf_contains,
    assert_pdf_pages,
    invoke,
    require_tool,
)

NOUN = "pdf"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# CREATE / CONVERT INTO PDF
# ──────────────────────────────────────────────────────────────────────────────

class TestFromHtml:
    def test_basic(self, runner: CliRunner, tmp_path: Path, sample_html_rich) -> None:
        out = tmp_path / "h.pdf"
        invoke(runner, NOUN, "from-html", str(sample_html_rich()), str(out))
        assert out.exists()


class TestFromMd:
    def test_reportlab(self, runner: CliRunner, tmp_path: Path, sample_md_rich) -> None:
        out = tmp_path / "m.pdf"
        invoke(runner, NOUN, "from-md", str(sample_md_rich()), str(out),
               "--engine", "reportlab")
        assert out.exists()
        assert_pdf_contains(out, "Top Heading")


class TestConvert:
    def test_help(self, runner: CliRunner) -> None:
        # convert needs EPUB/XPS/CBZ — fixtures unavailable; help-coverage suffices.
        res = invoke(runner, NOUN, "convert", "--help")
        assert_ok(res)


class TestQr:
    def test_value(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "qr.pdf"
        invoke(runner, NOUN, "qr", "--value", "https://example.com", "-o", str(out))
        assert out.exists()


class TestBarcode:
    def test_code128(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "bc.pdf"
        invoke(runner, NOUN, "barcode", "--type", "code128",
               "--value", "12345", "-o", str(out))
        assert out.exists()


# ──────────────────────────────────────────────────────────────────────────────
# READ / EXTRACT
# ──────────────────────────────────────────────────────────────────────────────

class TestInfo:
    def test_json(self, runner: CliRunner, sample_pdf) -> None:
        data = assert_json_output(invoke(runner, NOUN, "info", str(sample_pdf()), "--json"))
        assert "page_count" in data or "pages" in data


class TestExtractText:
    def test_default(self, runner: CliRunner, sample_pdf) -> None:
        res = invoke(runner, NOUN, "extract-text", str(sample_pdf()))
        assert_ok(res)
        assert "Page 1" in res.output

    def test_pages(self, runner: CliRunner, sample_pdf) -> None:
        res = invoke(runner, NOUN, "extract-text", str(sample_pdf(pages=3)),
                     "--pages", "2")
        assert_ok(res)
        assert "Page 2" in res.output


class TestExtractTables:
    def test_no_tables_clean_exit(self, runner: CliRunner, sample_pdf) -> None:
        res = invoke(runner, NOUN, "extract-tables", str(sample_pdf()))
        # Acceptable: 0 (writes empty), 3 (no-tables sentinel), 4 (error sentinel).
        assert res.exit_code in (0, 3, 4), res.output


class TestExtractImages:
    def test_no_images(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        outdir = tmp_path / "imgs"
        outdir.mkdir()
        res = invoke(runner, NOUN, "extract-images", str(sample_pdf()),
                     "--out", str(outdir))
        assert_ok(res)


class TestSearch:
    def test_term(self, runner: CliRunner, sample_pdf) -> None:
        data = assert_json_output(
            invoke(runner, NOUN, "search", str(sample_pdf(text="needle")),
                   "--term", "needle", "--json")
        )
        assert data.get("count", 0) > 0


class TestChars:
    def test_basic(self, runner: CliRunner, sample_pdf) -> None:
        res = invoke(runner, NOUN, "chars", str(sample_pdf()))
        assert_ok(res)


class TestWords:
    def test_basic(self, runner: CliRunner, sample_pdf) -> None:
        res = invoke(runner, NOUN, "words", str(sample_pdf()), "--json")
        assert_ok(res)


class TestShapes:
    def test_basic(self, runner: CliRunner, sample_pdf) -> None:
        res = invoke(runner, NOUN, "shapes", str(sample_pdf()), "--json")
        assert_ok(res)


class TestTablesDebug:
    def test_render(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        out = tmp_path / "debug.png"
        invoke(runner, NOUN, "tables-debug", str(sample_pdf()),
               "--page", "1", "-o", str(out))
        assert out.exists()


# ──────────────────────────────────────────────────────────────────────────────
# TRANSFORM
# ──────────────────────────────────────────────────────────────────────────────

class TestMerge:
    def test_two_files(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        a = sample_pdf(name="a.pdf", pages=2)
        b = sample_pdf(name="b.pdf", pages=3)
        out = tmp_path / "m.pdf"
        invoke(runner, NOUN, "merge", str(a), str(b), "-o", str(out))
        assert_pdf_pages(out, 5)


class TestSplit:
    def test_per_page(self, runner: CliRunner, sample_pdf_multipage, tmp_path: Path) -> None:
        outdir = tmp_path / "split"
        outdir.mkdir()
        invoke(runner, NOUN, "split", str(sample_pdf_multipage()),
               "--per-page", "--out-dir", str(outdir))
        assert len(list(outdir.glob("*.pdf"))) == 5


class TestRotate:
    def test_180(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        out = tmp_path / "r.pdf"
        invoke(runner, NOUN, "rotate", str(sample_pdf()), "--by", "180", "-o", str(out))
        assert out.exists()


class TestCrop:
    def test_box(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        out = tmp_path / "c.pdf"
        invoke(runner, NOUN, "crop", str(sample_pdf()),
               "--box", "0,0,400,500", "-o", str(out))
        assert out.exists()


class TestRender:
    def test_page1(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        out = tmp_path / "p1.png"
        invoke(runner, NOUN, "render", str(sample_pdf()), "--page", "1", "-o", str(out))
        assert out.exists()


class TestFlatten:
    def test_default(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        out = tmp_path / "f.pdf"
        invoke(runner, NOUN, "flatten", str(sample_pdf()), "-o", str(out))
        assert out.exists()


class TestStamp:
    def test_image(self, runner: CliRunner, sample_pdf, sample_png, tmp_path: Path) -> None:
        out = tmp_path / "s.pdf"
        invoke(runner, NOUN, "stamp", str(sample_pdf()),
               "--image", str(sample_png()), "--at", "BR",
               "--scale", "0.2", "-o", str(out))
        assert out.exists()


class TestWatermark:
    def test_text(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        out = tmp_path / "wm.pdf"
        invoke(runner, NOUN, "watermark", str(sample_pdf()),
               "--text", "DRAFT", "-o", str(out))
        assert out.exists()


class TestRedact:
    def test_regex(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        out = tmp_path / "red.pdf"
        invoke(runner, NOUN, "redact", str(sample_pdf(text="secret-data")),
               "--regex", r"secret-\w+", "-o", str(out))
        assert out.exists()


class TestEncryptDecrypt:
    def test_round_trip(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        enc = tmp_path / "e.pdf"
        dec = tmp_path / "d.pdf"
        invoke(runner, NOUN, "encrypt", str(sample_pdf()),
               "--password", "p4ss", "-o", str(enc))
        invoke(runner, NOUN, "decrypt", str(enc),
               "--password", "p4ss", "-o", str(dec))
        assert dec.exists()


class TestOcr:
    def test_help(self, runner: CliRunner) -> None:
        # OCR needs tesseract + an image-only PDF; help-coverage suffices unit-side.
        res = invoke(runner, NOUN, "ocr", "--help")
        assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# ANNOTATE / BOOKMARK / TOC / FORM / ATTACH
# ──────────────────────────────────────────────────────────────────────────────

class TestAnnotate:
    def test_highlight(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        out = tmp_path / "a.pdf"
        invoke(runner, NOUN, "annotate", str(sample_pdf(text="hello world")),
               "--page", "1", "--highlight", "hello", "-o", str(out))
        assert out.exists()


class TestAttach:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "attach", "--help")
        assert_ok(res)
        assert "list" in res.output

    def test_add_and_list(self, runner: CliRunner, sample_pdf,
                          sample_csv, tmp_path: Path) -> None:
        out = tmp_path / "with-att.pdf"
        invoke(runner, NOUN, "attach", "add", str(sample_pdf()),
               "--file", str(sample_csv()), "-o", str(out))
        res = invoke(runner, NOUN, "attach", "list", str(out), "--json")
        assert_ok(res)


class TestBookmark:
    def test_add(self, runner: CliRunner, sample_pdf_multipage, tmp_path: Path) -> None:
        out = tmp_path / "bm.pdf"
        invoke(runner, NOUN, "bookmark", "add", str(sample_pdf_multipage()),
               "--title", "Chapter One", "--page", "2", "-o", str(out))
        assert out.exists()


class TestToc:
    def test_get_empty(self, runner: CliRunner, sample_pdf) -> None:
        res = invoke(runner, NOUN, "toc", "get", str(sample_pdf()), "--json")
        assert_ok(res)


class TestForm:
    def test_list(self, runner: CliRunner, sample_pdf) -> None:
        res = invoke(runner, NOUN, "form", "list", str(sample_pdf()), "--json")
        assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# JOURNAL / LABELS / LAYER
# ──────────────────────────────────────────────────────────────────────────────

class TestJournal:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "journal", "--help")
        assert_ok(res)
        for sub in ("start", "commit", "rollback", "status"):
            assert sub in res.output


class TestLabels:
    def test_set(self, runner: CliRunner, sample_pdf_multipage, tmp_path: Path) -> None:
        out = tmp_path / "l.pdf"
        invoke(runner, NOUN, "labels", "set", str(sample_pdf_multipage()),
               "--rule", "i:1-2,1:3-end", "-o", str(out))
        assert out.exists()


class TestLayer:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "layer", "--help")
        assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# META
# ──────────────────────────────────────────────────────────────────────────────

class TestMeta:
    def test_get(self, runner: CliRunner, sample_pdf) -> None:
        res = invoke(runner, NOUN, "meta", "get", str(sample_pdf()), "--json")
        assert_ok(res)

    def test_set(self, runner: CliRunner, sample_pdf, tmp_path: Path) -> None:
        out = tmp_path / "m.pdf"
        invoke(runner, NOUN, "meta", "set", str(sample_pdf()),
               "--title", "MyTitle", "-o", str(out))
        assert out.exists()
