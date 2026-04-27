"""Unit tests for `claw html`."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from .._helpers import assert_ok, invoke

NOUN = "html"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


class TestSelect:
    def test_css(self, runner: CliRunner, sample_html_rich) -> None:
        res = invoke(runner, NOUN, "select", str(sample_html_rich()),
                     "--css", "h1", "--text")
        assert_ok(res)
        assert "Main Headline" in res.output


class TestText:
    def test_extract(self, runner: CliRunner, sample_html_rich) -> None:
        res = invoke(runner, NOUN, "text", str(sample_html_rich()), "--strip")
        assert_ok(res)
        assert "Main Headline" in res.output


class TestStrip:
    def test_remove_scripts(self, runner: CliRunner, sample_html_rich, tmp_path: Path) -> None:
        out = tmp_path / "clean.html"
        invoke(runner, NOUN, "strip", str(sample_html_rich()),
               "--css", "script", "--css", "style", "--out", str(out))
        text = out.read_text(encoding="utf-8")
        assert "<script" not in text


class TestUnwrap:
    def test_basic(self, runner: CliRunner, sample_html_rich, tmp_path: Path) -> None:
        out = tmp_path / "u.html"
        invoke(runner, NOUN, "unwrap", str(sample_html_rich()),
               "--css", "header", "--out", str(out))
        assert out.exists()


class TestWrap:
    def test_basic(self, runner: CliRunner, sample_html_rich, tmp_path: Path) -> None:
        out = tmp_path / "w.html"
        invoke(runner, NOUN, "wrap", str(sample_html_rich()),
               "--css", "h1", "--with", "section.intro", "--out", str(out))
        assert out.exists()


class TestSanitize:
    def test_allow_list(self, runner: CliRunner, sample_html_rich, tmp_path: Path) -> None:
        out = tmp_path / "s.html"
        invoke(runner, NOUN, "sanitize", str(sample_html_rich()),
               "--allow", "p,h1,h2,a", "--out", str(out))
        text = out.read_text(encoding="utf-8")
        assert "<script" not in text


class TestAbsolutize:
    def test_relative_to_absolute(self, runner: CliRunner, sample_html_rich, tmp_path: Path) -> None:
        out = tmp_path / "abs.html"
        invoke(runner, NOUN, "absolutize", str(sample_html_rich()),
               "--base", "https://example.com", "--out", str(out))
        text = out.read_text(encoding="utf-8")
        assert "https://example.com/rel/path" in text


class TestRewrite:
    def test_url_substring(self, runner: CliRunner, sample_html_rich, tmp_path: Path) -> None:
        out = tmp_path / "r.html"
        invoke(runner, NOUN, "rewrite", str(sample_html_rich()),
               "--from", "/img/", "--to", "/cdn/", "--out", str(out))
        text = out.read_text(encoding="utf-8")
        assert "/cdn/photo.jpg" in text


class TestReplace:
    def test_text(self, runner: CliRunner, sample_html_rich, tmp_path: Path) -> None:
        out = tmp_path / "rp.html"
        invoke(runner, NOUN, "replace", str(sample_html_rich()),
               "--css", "h1", "--text", "REPLACED", "--out", str(out))
        text = out.read_text(encoding="utf-8")
        assert "REPLACED" in text


class TestFmt:
    def test_pretty(self, runner: CliRunner, sample_html, tmp_path: Path) -> None:
        out = tmp_path / "p.html"
        invoke(runner, NOUN, "fmt", str(sample_html()), "--out", str(out))
        assert out.exists()


class TestDiagnose:
    def test_basic(self, runner: CliRunner, sample_html) -> None:
        res = invoke(runner, NOUN, "diagnose", str(sample_html()))
        assert_ok(res)
