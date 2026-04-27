"""Unit tests for `claw docx`."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from .._helpers import (
    assert_docx_has_text,
    assert_docx_heading,
    assert_json_output,
    assert_ok,
    invoke,
    require_tool,
)

NOUN = "docx"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────────────────────────────────────

class TestNew:
    def test_minimum_args(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.docx"
        invoke(runner, NOUN, "new", str(out))
        assert out.exists()

    def test_overwrite_protection(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.docx"
        out.write_bytes(b"")
        res = invoke(runner, NOUN, "new", str(out))
        assert res.exit_code != 0


class TestFromMd:
    def test_basic(self, runner: CliRunner, tmp_path: Path, sample_md_rich) -> None:
        require_tool("pandoc")
        out = tmp_path / "x.docx"
        invoke(runner, NOUN, "from-md", str(out), "--data", str(sample_md_rich()))
        assert out.exists()
        assert_docx_heading(out, "Top Heading", level=1)


# ──────────────────────────────────────────────────────────────────────────────
# READ / INSPECT
# ──────────────────────────────────────────────────────────────────────────────

class TestRead:
    def test_text(self, runner: CliRunner, sample_docx) -> None:
        res = invoke(runner, NOUN, "read", str(sample_docx()), "--text")
        assert_ok(res)
        assert "Title" in res.output

    def test_json(self, runner: CliRunner, sample_docx) -> None:
        data = assert_json_output(invoke(runner, NOUN, "read", str(sample_docx()), "--json"))
        assert isinstance(data, (list, dict))

    def test_headings(self, runner: CliRunner, sample_docx) -> None:
        res = invoke(runner, NOUN, "read", str(sample_docx()), "--headings")
        assert_ok(res)


class TestComments:
    def test_dump_empty(self, runner: CliRunner, sample_docx) -> None:
        res = invoke(runner, NOUN, "comments", "dump", str(sample_docx()), "--json")
        assert_ok(res)


class TestDiff:
    def test_no_revisions(self, runner: CliRunner, sample_docx) -> None:
        res = invoke(runner, NOUN, "diff", str(sample_docx()), "--json")
        assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# EDIT
# ──────────────────────────────────────────────────────────────────────────────

class TestAddHeading:
    def test_basic(self, runner: CliRunner, sample_docx) -> None:
        p = sample_docx()
        invoke(runner, NOUN, "add-heading", str(p),
               "--text", "Section Two", "--level", "2", "--force")
        assert_docx_heading(p, "Section Two", level=2)


class TestAddParagraph:
    def test_bold(self, runner: CliRunner, sample_docx) -> None:
        p = sample_docx()
        invoke(runner, NOUN, "add-paragraph", str(p),
               "--text", "appended para", "--bold", "--force")
        assert_docx_has_text(p, "appended para")


class TestAddTable:
    def test_with_csv(self, runner: CliRunner, sample_docx, sample_csv) -> None:
        invoke(runner, NOUN, "add-table", str(sample_docx()),
               "--data", str(sample_csv()), "--header", "--force")


class TestAddImage:
    def test_inline(self, runner: CliRunner, sample_docx, sample_png) -> None:
        invoke(runner, NOUN, "add-image", str(sample_docx()),
               "--image", str(sample_png()), "--width", "2.0", "--force")


class TestInsert:
    def test_pagebreak_before(self, runner: CliRunner, sample_docx) -> None:
        invoke(runner, NOUN, "insert", "pagebreak", str(sample_docx()),
               "--before", "Title", "--force")


class TestHyperlink:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "hyperlink", "--help")
        assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# FORMAT / STYLE
# ──────────────────────────────────────────────────────────────────────────────

class TestStyle:
    def test_apply_existing(self, runner: CliRunner, sample_docx) -> None:
        invoke(runner, NOUN, "style", "apply", str(sample_docx()),
               "--name", "Normal", "--all-matching-style", "Normal", "--force")

    def test_define(self, runner: CliRunner, sample_docx) -> None:
        invoke(runner, NOUN, "style", "define", str(sample_docx()),
               "--name", "MyStyle", "--font", "Arial", "--size", "12", "--force")


class TestSection:
    def test_landscape(self, runner: CliRunner, sample_docx) -> None:
        invoke(runner, NOUN, "section", "add", str(sample_docx()),
               "--orientation", "landscape", "--force")


class TestHeader:
    def test_set_text(self, runner: CliRunner, sample_docx) -> None:
        invoke(runner, NOUN, "header", str(sample_docx()), "--text", "HDR", "--force")


class TestFooter:
    def test_set_text(self, runner: CliRunner, sample_docx) -> None:
        invoke(runner, NOUN, "footer", str(sample_docx()), "--text", "FTR", "--force")


class TestToc:
    def test_insert(self, runner: CliRunner, sample_docx) -> None:
        invoke(runner, NOUN, "toc", str(sample_docx()), "--force")


class TestTable:
    def test_help(self, runner: CliRunner) -> None:
        # `table` subgroup — `fit` requires a table at --index, skip integration
        # to keep the test fixture-light; help-coverage already validates form.
        res = invoke(runner, NOUN, "table", "--help")
        assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# META / CUSTOM XML
# ──────────────────────────────────────────────────────────────────────────────

class TestMeta:
    def test_get(self, runner: CliRunner, sample_docx) -> None:
        res = invoke(runner, NOUN, "meta", "get", str(sample_docx()))
        assert_ok(res)


class TestCustomXml:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "custom-xml", "--help")
        assert_ok(res)
