"""Unit tests for `claw email` (Gmail). Help-only — no live API."""

from __future__ import annotations

from click.testing import CliRunner

from .._helpers import assert_ok, invoke

NOUN = "email"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


class TestSend:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "send", "--help")
        assert_ok(res)
        assert "--to" in res.output
        assert "--subject" in res.output


class TestDraft:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "draft", "--help"))


class TestReply:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "reply", "--help"))


class TestForward:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "forward", "--help"))


class TestSearch:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "search", "--help"))


class TestDownloadAttachment:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "download-attachment", "--help"))
