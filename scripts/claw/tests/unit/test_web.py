"""Unit tests for `claw web` — uses local http.server to avoid network."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from .._helpers import (
    assert_json_output,
    assert_ok,
    invoke,
    local_http_server,
)

NOUN = "web"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


class TestFetch:
    def test_basic(self, runner: CliRunner, tmp_path: Path, sample_html_rich) -> None:
        sample_html_rich(name="index.html")
        with local_http_server(tmp_path) as base:
            res = invoke(runner, NOUN, "fetch", f"{base}/index.html")
            assert_ok(res)
            assert "Main Headline" in res.output

    def test_to_file(self, runner: CliRunner, tmp_path: Path, sample_html) -> None:
        sample_html(name="x.html")
        out = tmp_path / "out.html"
        with local_http_server(tmp_path) as base:
            invoke(runner, NOUN, "fetch", f"{base}/x.html", "--out", str(out))
        assert out.exists()


class TestExtract:
    def test_url(self, runner: CliRunner, tmp_path: Path, sample_html_rich) -> None:
        sample_html_rich(name="article.html")
        with local_http_server(tmp_path) as base:
            res = invoke(runner, NOUN, "extract", f"{base}/article.html",
                         "--format", "text")
        assert_ok(res)


class TestLinks:
    def test_extract_links(self, runner: CliRunner, tmp_path: Path, sample_html_rich) -> None:
        sample_html_rich(name="page.html")
        with local_http_server(tmp_path) as base:
            res = invoke(runner, NOUN, "links", f"{base}/page.html",
                         "--format", "json", "--unique")
        assert_ok(res)


class TestSnapshot:
    def test_basic(self, runner: CliRunner, tmp_path: Path, sample_html_rich) -> None:
        sample_html_rich(name="snap.html")
        out = tmp_path / "snap.html"
        with local_http_server(tmp_path) as base:
            invoke(runner, NOUN, "snapshot", f"{base}/snap.html", "--out", str(out))
        assert out.exists()


class TestTable:
    def test_to_csv(self, runner: CliRunner, tmp_path: Path, sample_html_rich) -> None:
        sample_html_rich(name="t.html")
        out = tmp_path / "t.csv"
        with local_http_server(tmp_path) as base:
            invoke(runner, NOUN, "table", f"{base}/t.html", "--out", str(out))
        assert out.exists()
