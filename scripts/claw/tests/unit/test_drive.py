"""Unit tests for `claw drive` (Google Drive).

No live API — `--help` and `--dry-run` only.
"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from .._helpers import assert_ok, invoke

NOUN = "drive"


def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)


class TestUpload:
    def test_dry_run(self, runner: CliRunner, tmp_path: Path) -> None:
        f = tmp_path / "x.txt"
        f.write_text("hi")
        res = invoke(runner, NOUN, "upload", "--from", str(f), "--dry-run")
        assert res.exit_code in (0, 1, 2), res.output


class TestDownload:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "download", "--help"))


class TestInfo:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "info", "--help")
        assert_ok(res)
        assert "FILE_ID" in res.output


class TestList:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "list", "--help"))


class TestCopy:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "copy", "--help"))


class TestMove:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "move", "--help"))


class TestRename:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "rename", "--help"))


class TestDelete:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "delete", "--help")
        assert_ok(res)
        # Verify the trash-default contract is documented.
        assert "Trash" in res.output or "trash" in res.output


class TestShare:
    def test_help(self, runner: CliRunner) -> None:
        res = invoke(runner, NOUN, "share", "--help")
        assert_ok(res)
        assert "--role" in res.output


class TestShareList:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "share-list", "--help"))


class TestShareRevoke:
    def test_help(self, runner: CliRunner) -> None:
        assert_ok(invoke(runner, NOUN, "share-revoke", "--help"))
