"""Unit tests for `claw xml`."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from .._helpers import assert_json_output, assert_ok, invoke

NOUN = "xml"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


class TestXpath:
    def test_text(self, runner: CliRunner, sample_xml) -> None:
        res = invoke(runner, NOUN, "xpath", str(sample_xml()), "//a/text()", "--text")
        assert_ok(res)
        assert "v1" in res.output


class TestXslt:
    def test_basic(self, runner: CliRunner, sample_xml, tmp_path: Path) -> None:
        xsl = tmp_path / "t.xsl"
        xsl.write_text(
            '<?xml version="1.0"?>'
            '<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">'
            '<xsl:template match="/"><out>'
            '<xsl:for-each select="//a"><x><xsl:value-of select="."/></x></xsl:for-each>'
            '</out></xsl:template></xsl:stylesheet>',
            encoding="utf-8",
        )
        out = tmp_path / "o.xml"
        invoke(runner, NOUN, "xslt", str(sample_xml()), str(xsl), "--out", str(out))
        assert out.exists()


class TestValidate:
    def test_no_schema_errors(self, runner: CliRunner, sample_xml) -> None:
        # No schema → expect non-zero (must specify --xsd/--rng/etc.)
        res = invoke(runner, NOUN, "validate", str(sample_xml()))
        assert res.exit_code != 0


class TestCanonicalize:
    def test_basic(self, runner: CliRunner, sample_xml, tmp_path: Path) -> None:
        out = tmp_path / "c.xml"
        invoke(runner, NOUN, "canonicalize", str(sample_xml()), "--out", str(out))
        assert out.exists()


class TestFmt:
    def test_pretty(self, runner: CliRunner, sample_xml, tmp_path: Path) -> None:
        out = tmp_path / "f.xml"
        invoke(runner, NOUN, "fmt", str(sample_xml()), "--indent", "2", "--out", str(out))
        assert out.exists()


class TestToJson:
    def test_literal(self, runner: CliRunner, sample_xml) -> None:
        res = invoke(runner, NOUN, "to-json", str(sample_xml()))
        assert_ok(res)


class TestStreamXpath:
    def test_basic(self, runner: CliRunner, sample_xml) -> None:
        res = invoke(runner, NOUN, "stream-xpath", str(sample_xml()),
                     "text()", "--tag", "a", "--text")
        assert_ok(res)
