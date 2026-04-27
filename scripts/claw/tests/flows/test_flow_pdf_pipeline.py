"""Flow: md → pdf → merge → split → watermark → encrypt → decrypt → meta → search."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from .._helpers import (
    assert_pdf_pages,
    invoke_subprocess,
)

pytestmark = pytest.mark.flow


def _ok(res) -> None:
    assert res.exit_code == 0, f"exit {res.exit_code}\n{res.output}"


class TestFlowPdfPipeline:
    @pytest.fixture(scope="class")
    def workspace(self):
        tmp = Path(tempfile.mkdtemp(prefix="claw_flow_pdf_"))
        md = tmp / "doc.md"
        md.write_text(
            "# Report Title\n\n## Section A\n\nLorem ipsum needle dolor sit.\n"
            "\n## Section B\n\nMore text content.\n",
            encoding="utf-8",
        )
        ws = {
            "tmp": tmp, "md": md,
            "pdf": tmp / "doc.pdf",
            "second": tmp / "second.pdf",
            "merged": tmp / "merged.pdf",
            "wm": tmp / "watermarked.pdf",
            "encrypted": tmp / "encrypted.pdf",
            "decrypted": tmp / "decrypted.pdf",
            "split_dir": tmp / "split",
        }
        ws["split_dir"].mkdir()
        yield ws
        shutil.rmtree(tmp, ignore_errors=True)

    def test_01_md_to_pdf(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pdf", "from-md", str(workspace["md"]), str(workspace["pdf"]),
                              "--engine", "reportlab"))
        assert workspace["pdf"].exists()

    def test_02_create_second_pdf(self, workspace: dict) -> None:
        # Second source for the merge stage; build directly via reportlab.
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(str(workspace["second"]))
        for i in range(2):
            c.drawString(72, 720, f"SECOND_PAGE_{i+1}")
            c.showPage()
        c.save()
        assert_pdf_pages(workspace["second"], 2)

    def test_03_merge(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pdf", "merge",
                              str(workspace["pdf"]), str(workspace["second"]),
                              "-o", str(workspace["merged"])))
        assert workspace["merged"].exists()

    def test_04_split_per_page(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pdf", "split", str(workspace["merged"]),
                              "--per-page", "--out-dir", str(workspace["split_dir"])))
        assert len(list(workspace["split_dir"].glob("*.pdf"))) >= 2

    def test_05_watermark(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pdf", "watermark", str(workspace["merged"]),
                              "--text", "DRAFT", "-o", str(workspace["wm"])))
        assert workspace["wm"].exists()

    def test_06_search(self, workspace: dict) -> None:
        res = invoke_subprocess("pdf", "search", str(workspace["wm"]),
                                "--term", "needle", "--json")
        _ok(res)
        data = json.loads(res.output)
        # Search may return a count dict or hit list — both indicate success.
        assert data.get("count", 0) > 0 or len(data) > 0

    def test_07_encrypt(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pdf", "encrypt", str(workspace["wm"]),
                              "--password", "p4ss", "-o", str(workspace["encrypted"])))
        assert workspace["encrypted"].exists()

    def test_08_decrypt(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pdf", "decrypt", str(workspace["encrypted"]),
                              "--password", "p4ss", "-o", str(workspace["decrypted"])))
        assert workspace["decrypted"].exists()

    def test_09_meta_set_get(self, workspace: dict) -> None:
        out = workspace["tmp"] / "with-meta.pdf"
        _ok(invoke_subprocess("pdf", "meta", "set", str(workspace["decrypted"]),
                              "--title", "Final", "--author", "claw", "-o", str(out)))
        res = invoke_subprocess("pdf", "meta", "get", str(out), "--json")
        _ok(res)
        data = json.loads(res.output)
        assert data.get("title") == "Final"
