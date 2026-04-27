"""Flow: local HTTP server → web fetch → web extract → html sanitize → web table → xlsx import."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from .._helpers import (
    invoke_subprocess,
    local_http_server,
)

pytestmark = pytest.mark.flow


def _ok(res) -> None:
    assert res.exit_code == 0, f"exit {res.exit_code}\n{res.output}"


class TestFlowWebHtml:
    @pytest.fixture(scope="class")
    def workspace(self):
        tmp = Path(tempfile.mkdtemp(prefix="claw_flow_web_"))
        page = tmp / "article.html"
        page.write_text(
            "<html><head><title>Article</title></head><body>"
            "<header><nav><a href='/home'>Home</a></nav></header>"
            "<article>"
            "<h1>Big Headline</h1>"
            "<p>The lead paragraph introduces the topic in detail.</p>"
            "<table><thead><tr><th>k</th><th>v</th></tr></thead>"
            "<tbody><tr><td>x</td><td>1</td></tr><tr><td>y</td><td>2</td></tr></tbody></table>"
            "<p><script>alert('xss')</script></p>"
            "</article></body></html>",
            encoding="utf-8",
        )
        ws = {"tmp": tmp, "page": page,
              "fetched": tmp / "fetched.html",
              "sanitized": tmp / "clean.html",
              "csv": tmp / "table.csv",
              "xlsx": tmp / "table.xlsx"}
        yield ws
        shutil.rmtree(tmp, ignore_errors=True)

    def test_01_fetch_local_url(self, workspace: dict) -> None:
        with local_http_server(workspace["tmp"]) as base:
            _ok(invoke_subprocess("web", "fetch", f"{base}/article.html",
                                   "--out", str(workspace["fetched"])))
        assert workspace["fetched"].exists()

    def test_02_sanitize_strip_scripts(self, workspace: dict) -> None:
        _ok(invoke_subprocess("html", "sanitize", str(workspace["fetched"]),
                              "--allow", "p,h1,h2,a,table,thead,tbody,tr,th,td",
                              "--out", str(workspace["sanitized"])))
        assert "<script" not in workspace["sanitized"].read_text(encoding="utf-8")

    def test_03_extract_text(self, workspace: dict) -> None:
        res = invoke_subprocess("html", "text", str(workspace["sanitized"]),
                                "--strip")
        _ok(res)
        assert "Big Headline" in res.output

    def test_04_table_to_csv(self, workspace: dict) -> None:
        with local_http_server(workspace["tmp"]) as base:
            _ok(invoke_subprocess("web", "table", f"{base}/article.html",
                                   "--out", str(workspace["csv"])))
        assert workspace["csv"].exists()

    def test_05_csv_to_xlsx(self, workspace: dict) -> None:
        _ok(invoke_subprocess("xlsx", "from-csv", str(workspace["xlsx"]),
                              str(workspace["csv"])))
        assert workspace["xlsx"].exists()
