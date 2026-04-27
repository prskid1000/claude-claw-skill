"""COPY-PASTE TEMPLATE — flow test skeleton.

A flow test exercises a multi-verb pipeline on real artifacts. Use this when a
new verb participates in a meaningful chain (e.g. ``csv → xlsx → chart → pdf``).

Conventions:
  * One ``TestFlow<Name>`` class per pipeline.
  * Stages are numbered methods (``test_01_*``, ``test_02_*``, ...). Pytest
    runs them in source order, so a failure at stage N short-circuits later
    stages — making the failure source obvious.
  * Stages share state via ``self.workspace`` (set up in a class-level
    ``setup_method`` or a class-scoped fixture).
  * Each stage asserts the artifact it produces — not just ``.exists()``.
  * A final ``test_99_full_smoke`` runs the whole chain in a single test for
    when an isolated re-run is needed.

Copy this file to ``tests/flows/test_flow_<area>.py`` and fill in.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from tests._helpers import (
    assert_ok,
    assert_pdf_pages,
    assert_xlsx_sheets,
    invoke,
    require_tool,
)

pytestmark = pytest.mark.flow


class TestFlowExample:
    """CSV → xlsx → styled → chart → pdf-rendered."""

    @pytest.fixture(autouse=True)
    def _workspace(self, tmp_path: Path, sample_csv) -> None:
        self.tmp = tmp_path
        self.csv = sample_csv(rows=10)
        self.xlsx = tmp_path / "report.xlsx"
        self.pdf = tmp_path / "report.pdf"

    # Stages run in source order (pytest collects definition-order).

    def test_01_csv_to_xlsx(self, runner: CliRunner) -> None:
        invoke(runner, "xlsx", "from-csv", str(self.xlsx), "--data", str(self.csv))
        assert_xlsx_sheets(self.xlsx, ["data"])

    def test_02_style_header(self, runner: CliRunner) -> None:
        invoke(
            runner, "xlsx", "style", str(self.xlsx),
            "--sheet", "data", "--range", "A1:C1",
            "--bold", "--color", "FFFFFF", "--fill", "1F4E78",
            "--force",
        )

    def test_03_render_to_pdf(self, runner: CliRunner) -> None:
        require_tool("soffice")
        invoke(runner, "xlsx", "to-pdf", str(self.xlsx), "--out", str(self.pdf))
        assert self.pdf.exists()
        assert_pdf_pages(self.pdf, 1)

    def test_99_full_smoke(self, runner: CliRunner, tmp_path: Path, sample_csv) -> None:
        """One-shot variant — runs the whole flow in isolation."""
        require_tool("soffice")
        csv = sample_csv(rows=5)
        xlsx = tmp_path / "smoke.xlsx"
        pdf = tmp_path / "smoke.pdf"
        invoke(runner, "xlsx", "from-csv", str(xlsx), "--data", str(csv))
        invoke(
            runner, "xlsx", "style", str(xlsx),
            "--sheet", "data", "--range", "A1:C1", "--bold", "--force",
        )
        invoke(runner, "xlsx", "to-pdf", str(xlsx), "--out", str(pdf))
        assert_pdf_pages(pdf, 1)
