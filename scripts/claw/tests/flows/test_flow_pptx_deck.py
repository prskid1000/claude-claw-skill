"""Flow: outline.md → from-outline → add-slide → add-table → add-chart → notes → meta."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from .._helpers import (
    assert_pptx_slides,
    invoke_subprocess,
)

pytestmark = pytest.mark.flow


def _ok(res) -> None:
    assert res.exit_code == 0, f"exit {res.exit_code}\n{res.output}"


class TestFlowPptxDeck:
    @pytest.fixture(scope="class")
    def workspace(self):
        tmp = Path(tempfile.mkdtemp(prefix="claw_flow_pptx_"))
        outline = tmp / "outline.md"
        outline.write_text(
            "# Quarterly Review\n\n"
            "## Q1 Highlights\n\n- thing one\n- thing two\n\n"
            "## Q2 Highlights\n\n- thing three\n",
            encoding="utf-8",
        )
        csv = tmp / "data.csv"
        csv.write_text("region,sales\nEMEA,100\nAPAC,150\nUS,200\n", encoding="utf-8")
        ws = {"tmp": tmp, "outline": outline, "csv": csv,
              "deck": tmp / "deck.pptx"}
        yield ws
        shutil.rmtree(tmp, ignore_errors=True)

    def test_01_from_outline(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pptx", "from-outline", str(workspace["deck"]),
                              "--data", str(workspace["outline"])))
        assert workspace["deck"].exists()
        assert_pptx_slides(workspace["deck"], 3)

    def test_02_add_slide(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pptx", "add-slide", str(workspace["deck"]),
                              "--title", "Appendix",
                              "--body", "- supporting data\n- references",
                              "--force"))
        assert_pptx_slides(workspace["deck"], 4)

    def test_03_add_table(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pptx", "add-table", str(workspace["deck"]),
                              "--slide", "2",
                              "--data", str(workspace["csv"]),
                              "--header", "--force"))

    def test_04_add_chart(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pptx", "add-chart", str(workspace["deck"]),
                              "--slide", "3", "--type", "bar",
                              "--data", str(workspace["csv"]),
                              "--title", "Sales", "--force"))

    def test_05_notes(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pptx", "notes", str(workspace["deck"]),
                              "--slide", "1", "--text", "Welcome the audience",
                              "--force"))

    def test_06_meta_set(self, workspace: dict) -> None:
        _ok(invoke_subprocess("pptx", "meta", "set", str(workspace["deck"]),
                              "--title", "Quarterly Review", "--force"))
        res = invoke_subprocess("pptx", "meta", "get", str(workspace["deck"]), "--json")
        _ok(res)
        data = json.loads(res.output)
        assert data.get("title") == "Quarterly Review"
