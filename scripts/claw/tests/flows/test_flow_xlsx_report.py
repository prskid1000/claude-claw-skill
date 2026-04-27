"""Flow: CSV → xlsx (build → metadata → query → freeze/filter/style/format/table/chart) → drive(dry).

Each numbered stage builds on the previous one's artifact. State is shared via
a class-scoped ``workspace`` dict; failure at stage N localizes the regression.

Uses ``invoke_subprocess`` rather than ``invoke`` (CliRunner) because chained
in-place writes to the same xlsx file leak ZipFile mmaps in the parent
process on Windows, which then breaks subsequent ``os.replace``s. Each
subprocess call cleanly releases all handles before returning.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from .._helpers import (
    assert_xlsx_sheets,
    invoke_subprocess,
)

pytestmark = pytest.mark.flow


def _ok(res) -> None:
    assert res.exit_code == 0, f"exit {res.exit_code}\n{res.output}"


def _json(res):
    _ok(res)
    return json.loads(res.output)


class TestFlowXlsxReport:
    @pytest.fixture(scope="class")
    def workspace(self):
        tmp = Path(tempfile.mkdtemp(prefix="claw_flow_xlsx_"))
        csv = tmp / "data.csv"
        csv.write_text(
            "a,b,c\n" + "\n".join(f"r{i},{i},{i*10}" for i in range(20)) + "\n",
            encoding="utf-8",
        )
        ws = {"tmp": tmp, "csv": csv, "xlsx": tmp / "report.xlsx"}
        yield ws
        shutil.rmtree(tmp, ignore_errors=True)

    def test_01_build_workbook_from_csv(self, workspace: dict) -> None:
        _ok(invoke_subprocess("xlsx", "from-csv",
                              str(workspace["xlsx"]), str(workspace["csv"])))
        assert_xlsx_sheets(workspace["xlsx"], ["data"])

    def test_02_set_metadata(self, workspace: dict) -> None:
        _ok(invoke_subprocess("xlsx", "meta", "set", str(workspace["xlsx"]),
                              "--title", "Quarterly Report", "--author", "claw", "--force"))
        meta = _json(invoke_subprocess("xlsx", "meta", "get",
                                        str(workspace["xlsx"]), "--json"))
        assert meta["title"] == "Quarterly Report"
        assert meta["creator"] == "claw"

    def test_03_query_count(self, workspace: dict) -> None:
        data = _json(invoke_subprocess("xlsx", "sql", str(workspace["xlsx"]),
                                        "SELECT count(*) AS n FROM data", "--json"))
        assert data[0]["n"] == 20

    def test_04_freeze_header_row(self, workspace: dict) -> None:
        _ok(invoke_subprocess("xlsx", "freeze", str(workspace["xlsx"]),
                              "--sheet", "data", "--rows", "1", "--force"))

    def test_05_filter_on_data_range(self, workspace: dict) -> None:
        _ok(invoke_subprocess("xlsx", "filter", str(workspace["xlsx"]),
                              "--sheet", "data", "--range", "A1:C21", "--force"))

    def test_06_style_header(self, workspace: dict) -> None:
        _ok(invoke_subprocess("xlsx", "style", str(workspace["xlsx"]),
                              "--sheet", "data", "--range", "A1:C1",
                              "--bold", "--color", "FFFFFF", "--fill", "1F4E78", "--force"))

    def test_07_format_number_column(self, workspace: dict) -> None:
        _ok(invoke_subprocess("xlsx", "format", str(workspace["xlsx"]),
                              "--sheet", "data", "--range", "B:B",
                              "--number-format", "#,##0", "--force"))

    def test_08_define_table(self, workspace: dict) -> None:
        _ok(invoke_subprocess("xlsx", "table", str(workspace["xlsx"]),
                              "--sheet", "data", "--range", "A1:C21",
                              "--name", "ReportData", "--force"))

    def test_09_add_chart(self, workspace: dict) -> None:
        _ok(invoke_subprocess("xlsx", "chart", str(workspace["xlsx"]),
                              "--sheet", "data", "--type", "bar",
                              "--data", "B2:B21", "--title", "Counts", "--force"))

    def test_10_drive_upload_dry_run(self, workspace: dict) -> None:
        res = invoke_subprocess("drive", "upload",
                                "--from", str(workspace["xlsx"]), "--dry-run")
        assert "Traceback" not in res.output
