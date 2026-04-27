"""Unit tests for `claw xlsx` — class per verb, validates artifacts."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from .._helpers import (
    assert_exit,
    assert_json_output,
    assert_ok,
    assert_xlsx_cell,
    assert_xlsx_sheets,
    invoke,
    require_tool,
)

NOUN = "xlsx"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)
    assert "Usage:" in res.output


# ──────────────────────────────────────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────────────────────────────────────

class TestNew:
    def test_minimum_args(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.xlsx"
        invoke(runner, NOUN, "new", str(out))
        assert out.exists()

    def test_with_sheets(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.xlsx"
        invoke(runner, NOUN, "new", str(out), "--sheet", "S1", "--sheet", "S2")
        assert_xlsx_sheets(out, ["S1", "S2"])

    def test_overwrite_without_force_errors(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.xlsx"
        out.write_bytes(b"")
        res = invoke(runner, NOUN, "new", str(out))
        assert res.exit_code != 0

    def test_force_overwrites(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.xlsx"
        out.write_bytes(b"")
        invoke(runner, NOUN, "new", str(out), "--force")
        assert out.stat().st_size > 0

    def test_mkdir_creates_parents(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "deep" / "nested" / "x.xlsx"
        invoke(runner, NOUN, "new", str(out), "--mkdir")
        assert out.exists()

    def test_dry_run_writes_nothing(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.xlsx"
        invoke(runner, NOUN, "new", str(out), "--dry-run")
        assert not out.exists()


class TestFromCsv:
    def test_minimum_args(self, runner: CliRunner, tmp_path: Path, sample_csv) -> None:
        out = tmp_path / "fc.xlsx"
        csv = sample_csv()
        invoke(runner, NOUN, "from-csv", str(out), str(csv))
        assert out.exists()

    def test_with_sheet_name(self, runner: CliRunner, tmp_path: Path, sample_csv) -> None:
        out = tmp_path / "fc.xlsx"
        invoke(runner, NOUN, "from-csv", str(out), str(sample_csv()), "--sheet", "Custom")
        assert_xlsx_sheets(out, ["Custom"])


class TestFromJson:
    def test_minimum_args(self, runner: CliRunner, tmp_path: Path, sample_json_rows) -> None:
        out = tmp_path / "fj.xlsx"
        invoke(runner, NOUN, "from-json", str(out), "--data", str(sample_json_rows()))
        assert out.exists()

    def test_with_flatten(self, runner: CliRunner, tmp_path: Path, sample_json_rows) -> None:
        out = tmp_path / "fj.xlsx"
        rows = sample_json_rows(rows=[{"a": {"x": 1}, "b": 2}])
        invoke(runner, NOUN, "from-json", str(out), "--data", str(rows), "--flatten")
        assert out.exists()


class TestFromHtml:
    def test_with_table(self, runner: CliRunner, tmp_path: Path) -> None:
        html = tmp_path / "t.html"
        html.write_text(
            "<html><body><table><tr><th>k</th><th>v</th></tr>"
            "<tr><td>a</td><td>1</td></tr></table></body></html>",
            encoding="utf-8",
        )
        out = tmp_path / "fh.xlsx"
        invoke(runner, NOUN, "from-html", str(out), "--data", str(html))
        assert out.exists()


class TestFromPdf:
    def test_with_table_pdf(self, runner: CliRunner, tmp_path: Path) -> None:
        # Build a PDF with a real grid (pdfplumber can detect lines).
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        pdf = tmp_path / "table.pdf"
        c = canvas.Canvas(str(pdf))
        x0, y0, dx, dy = 1 * inch, 6 * inch, 1.2 * inch, 0.4 * inch
        for r in range(4):
            for col in range(3):
                c.rect(x0 + col * dx, y0 - r * dy, dx, dy)
                c.drawString(x0 + col * dx + 4, y0 - r * dy + 8,
                             f"r{r}c{col}" if r else f"H{col}")
        c.showPage()
        c.save()
        out = tmp_path / "fp.xlsx"
        invoke(runner, NOUN, "from-pdf", str(out), str(pdf), "--strategy", "lines")
        assert out.exists()


# ──────────────────────────────────────────────────────────────────────────────
# READ / EXPORT
# ──────────────────────────────────────────────────────────────────────────────

class TestRead:
    def test_default(self, runner: CliRunner, sample_xlsx) -> None:
        res = invoke(runner, NOUN, "read", str(sample_xlsx()))
        assert_ok(res)

    def test_json_output(self, runner: CliRunner, sample_xlsx) -> None:
        data = assert_json_output(invoke(runner, NOUN, "read", str(sample_xlsx()), "--json"))
        assert isinstance(data, list)

    def test_csv_output(self, runner: CliRunner, sample_xlsx) -> None:
        res = invoke(runner, NOUN, "read", str(sample_xlsx()), "--csv")
        assert_ok(res)
        assert "a,b,c" in res.output

    def test_with_range(self, runner: CliRunner, sample_xlsx) -> None:
        res = invoke(runner, NOUN, "read", str(sample_xlsx()), "--range", "A1:B2", "--json")
        assert_ok(res)


class TestToCsv:
    def test_to_stdout(self, runner: CliRunner, sample_xlsx) -> None:
        res = invoke(runner, NOUN, "to-csv", str(sample_xlsx()), "--sheet", "Data")
        assert_ok(res)
        assert "a,b,c" in res.output

    def test_to_file(self, runner: CliRunner, tmp_path: Path, sample_xlsx) -> None:
        out = tmp_path / "out.csv"
        invoke(runner, NOUN, "to-csv", str(sample_xlsx()), "--sheet", "Data", "--out", str(out))
        assert out.exists()
        assert "a,b,c" in out.read_text(encoding="utf-8")


class TestToPdf:
    def test_basic(self, runner: CliRunner, tmp_path: Path, sample_xlsx) -> None:
        require_tool("soffice")
        out = tmp_path / "out.pdf"
        invoke(runner, NOUN, "to-pdf", str(sample_xlsx()), "--out", str(out))
        assert out.exists()


# ──────────────────────────────────────────────────────────────────────────────
# QUERY / STATS
# ──────────────────────────────────────────────────────────────────────────────

class TestSql:
    def test_basic(self, runner: CliRunner, sample_xlsx) -> None:
        data = assert_json_output(
            invoke(runner, NOUN, "sql", str(sample_xlsx()), "SELECT sum(b) AS s FROM Data", "--json")
        )
        assert "s" in data[0]


class TestStat:
    def test_basic(self, runner: CliRunner, sample_xlsx) -> None:
        res = invoke(runner, NOUN, "stat", str(sample_xlsx()), "--sheet", "Data")
        assert_ok(res)
        assert "mean" in res.output.lower() or "min" in res.output.lower()


# ──────────────────────────────────────────────────────────────────────────────
# WRITE / APPEND
# ──────────────────────────────────────────────────────────────────────────────

class TestAppend:
    def test_csv_into_existing_sheet(
        self, runner: CliRunner, sample_xlsx, sample_csv
    ) -> None:
        p = sample_xlsx()
        invoke(runner, NOUN, "append", str(p), "--sheet", "Data",
               "--data", str(sample_csv()), "--force")
        assert p.exists()

    def test_json_into_new_sheet(
        self, runner: CliRunner, sample_xlsx, sample_json_rows
    ) -> None:
        p = sample_xlsx()
        invoke(runner, NOUN, "append", str(p), "--sheet", "NewSheet",
               "--data", str(sample_json_rows()), "--force")
        assert_xlsx_sheets(p, ["NewSheet"])


# ──────────────────────────────────────────────────────────────────────────────
# FORMATTING
# ──────────────────────────────────────────────────────────────────────────────

class TestStyle:
    def test_bold_color(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "style", str(sample_xlsx()),
               "--sheet", "Data", "--range", "A1:C1",
               "--bold", "--color", "FF0000", "--force")

    def test_preset(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "style", str(sample_xlsx()),
               "--sheet", "Data", "--range", "A1:C1",
               "--preset", "header", "--force")


class TestFreeze:
    def test_rows(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "freeze", str(sample_xlsx()),
               "--sheet", "Data", "--rows", "1", "--force")

    def test_at(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "freeze", str(sample_xlsx()),
               "--sheet", "Data", "--at", "B2", "--force")


class TestFilter:
    def test_on(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "filter", str(sample_xlsx()),
               "--sheet", "Data", "--range", "A1:C4", "--force")

    def test_off(self, runner: CliRunner, sample_xlsx) -> None:
        # Apply then remove.
        p = sample_xlsx()
        invoke(runner, NOUN, "filter", str(p), "--sheet", "Data", "--range", "A1:C4", "--force")
        invoke(runner, NOUN, "filter", str(p), "--sheet", "Data", "--off", "--force")


class TestConditional:
    def test_cell_is(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "conditional", str(sample_xlsx()),
               "--sheet", "Data", "--range", "A2:C4",
               "--cell-is", "greaterThan:5", "--fill", "#00FF00", "--force")

    def test_color_scale(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "conditional", str(sample_xlsx()),
               "--sheet", "Data", "--range", "B2:B4",
               "--color-scale", "min:#F8696B,max:#63BE7B", "--force")


class TestFormat:
    def test_number_format(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "format", str(sample_xlsx()),
               "--sheet", "Data", "--range", "B2:B4",
               "--number-format", "0.00", "--force")


class TestTable:
    def test_register(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "table", str(sample_xlsx()),
               "--sheet", "Data", "--range", "A1:C4",
               "--name", "MyTable", "--force")


class TestChart:
    def test_bar(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "chart", str(sample_xlsx()),
               "--sheet", "Data", "--type", "bar", "--data", "B2:B4", "--force")


class TestValidate:
    def test_list(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "validate", str(sample_xlsx()),
               "--sheet", "Data", "--range", "A2:A4",
               "--type", "list", "--values", "x,y,z", "--force")


# ──────────────────────────────────────────────────────────────────────────────
# DEFINED NAMES, META, PIVOTS (subgroups)
# ──────────────────────────────────────────────────────────────────────────────

class TestName:
    def test_add(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "name", "add", str(sample_xlsx()),
               "--name", "MyRange", "--refers-to", "=Data!$A$1:$A$3", "--force")


class TestMeta:
    def test_get(self, runner: CliRunner, sample_xlsx) -> None:
        data = assert_json_output(
            invoke(runner, NOUN, "meta", "get", str(sample_xlsx()), "--json")
        )
        assert "creator" in data

    def test_set(self, runner: CliRunner, sample_xlsx) -> None:
        p = sample_xlsx()
        invoke(runner, NOUN, "meta", "set", str(p), "--title", "MyTitle", "--force")
        data = assert_json_output(invoke(runner, NOUN, "meta", "get", str(p), "--json"))
        assert data.get("title") == "MyTitle"


class TestPivots:
    def test_list_empty(self, runner: CliRunner, sample_xlsx) -> None:
        res = invoke(runner, NOUN, "pivots", "list", str(sample_xlsx()))
        assert_ok(res)


# ──────────────────────────────────────────────────────────────────────────────
# PRINT, PROTECT, RICHTEXT, IMAGE
# ──────────────────────────────────────────────────────────────────────────────

class TestPrintSetup:
    def test_orientation(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "print-setup", str(sample_xlsx()),
               "--sheet", "Data", "--orientation", "landscape", "--force")


class TestProtect:
    def test_apply_sheet(self, runner: CliRunner, sample_xlsx) -> None:
        invoke(runner, NOUN, "protect", str(sample_xlsx()),
               "--scope", "sheet", "--sheet", "Data", "--password", "x", "--force")

    def test_clear(self, runner: CliRunner, sample_xlsx) -> None:
        p = sample_xlsx()
        invoke(runner, NOUN, "protect", str(p),
               "--scope", "sheet", "--sheet", "Data", "--password", "x", "--force")
        invoke(runner, NOUN, "protect", str(p),
               "--scope", "sheet", "--sheet", "Data", "--clear", "--force")


class TestRichtext:
    def test_set(self, runner: CliRunner, sample_xlsx) -> None:
        # `richtext set` — best-effort check that the verb runs; spec is open-ended.
        res = invoke(runner, NOUN, "richtext", "set", "--help")
        assert_ok(res)


class TestImage:
    def test_add(self, runner: CliRunner, sample_xlsx, sample_png) -> None:
        p = sample_xlsx()
        png = sample_png()
        invoke(runner, NOUN, "image", "add", str(p),
               "--sheet", "Data", "--at", "E2", "--image", str(png), "--force")
