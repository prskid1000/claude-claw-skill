"""Flow: new docx → headings → paragraphs → table → image → header/footer → toc → meta."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from .._helpers import (
    assert_docx_has_text,
    assert_docx_heading,
    invoke_subprocess,
)

pytestmark = pytest.mark.flow


def _ok(res) -> None:
    assert res.exit_code == 0, f"exit {res.exit_code}\n{res.output}"


class TestFlowDocxAuthoring:
    @pytest.fixture(scope="class")
    def workspace(self):
        tmp = Path(tempfile.mkdtemp(prefix="claw_flow_docx_"))
        # Make a CSV + PNG fixture for the table/image stages.
        csv = tmp / "t.csv"
        csv.write_text("col1,col2\nx,1\ny,2\n", encoding="utf-8")
        png = tmp / "logo.png"
        from PIL import Image
        Image.new("RGB", (100, 50), (180, 30, 30)).save(png, format="PNG")
        ws = {"tmp": tmp, "csv": csv, "png": png, "docx": tmp / "doc.docx"}
        yield ws
        shutil.rmtree(tmp, ignore_errors=True)

    def test_01_new(self, workspace: dict) -> None:
        _ok(invoke_subprocess("docx", "new", str(workspace["docx"])))
        assert workspace["docx"].exists()

    def test_02_add_heading(self, workspace: dict) -> None:
        _ok(invoke_subprocess("docx", "add-heading", str(workspace["docx"]),
                              "--text", "Main Section", "--level", "1", "--force"))
        assert_docx_heading(workspace["docx"], "Main Section", level=1)

    def test_03_add_paragraph(self, workspace: dict) -> None:
        _ok(invoke_subprocess("docx", "add-paragraph", str(workspace["docx"]),
                              "--text", "Body content here", "--bold", "--force"))
        assert_docx_has_text(workspace["docx"], "Body content here")

    def test_04_add_subheading(self, workspace: dict) -> None:
        _ok(invoke_subprocess("docx", "add-heading", str(workspace["docx"]),
                              "--text", "Sub Section", "--level", "2", "--force"))

    def test_05_add_table(self, workspace: dict) -> None:
        _ok(invoke_subprocess("docx", "add-table", str(workspace["docx"]),
                              "--data", str(workspace["csv"]), "--header", "--force"))

    def test_06_add_image(self, workspace: dict) -> None:
        _ok(invoke_subprocess("docx", "add-image", str(workspace["docx"]),
                              "--image", str(workspace["png"]),
                              "--width", "1.5", "--force"))

    def test_07_set_header(self, workspace: dict) -> None:
        _ok(invoke_subprocess("docx", "header", str(workspace["docx"]),
                              "--text", "Page Header", "--force"))

    def test_08_set_footer(self, workspace: dict) -> None:
        _ok(invoke_subprocess("docx", "footer", str(workspace["docx"]),
                              "--text", "Page Footer", "--force"))

    def test_09_insert_toc(self, workspace: dict) -> None:
        _ok(invoke_subprocess("docx", "toc", str(workspace["docx"]), "--force"))

    def test_10_get_metadata(self, workspace: dict) -> None:
        res = invoke_subprocess("docx", "meta", "get", str(workspace["docx"]))
        _ok(res)
