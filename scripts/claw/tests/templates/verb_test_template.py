"""COPY-PASTE TEMPLATE — copy this file to ``tests/unit/test_<noun>.py``.

Conventions:
  * One ``Test<VerbName>`` class per verb (PascalCase).
  * Inside each class:
      - ``test_minimum_args``        — required args only, happy path
      - ``test_with_<flag>``         — one method per high-value flag
      - ``test_overwrite_protection``— `--force` / no-`--force` contract
      - ``test_invalid_input``       — bogus inputs exit !=0 cleanly
  * Use ``invoke()`` from ``tests._helpers`` — it asserts no traceback.
  * Use ``assert_ok`` / ``assert_exit`` / ``assert_json_output`` for exit-code
    assertions; they dump stdout on failure for debug-ability.
  * Validate artifacts (file actually created, content actually correct) with
    ``assert_pdf_pages``, ``assert_xlsx_sheets``, etc. — not just ``.exists()``.

The discovery-driven coverage tests in ``tests/coverage/`` already verify that
every verb is invokable and every flag is parseable — so unit tests focus on
*behavior*, not exhaustive flag enumeration.
"""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from tests._helpers import (
    assert_image_dims,
    assert_json_output,
    assert_ok,
    assert_pdf_pages,
    assert_xlsx_sheets,
    invoke,
    require_tool,
)

NOUN = "xlsx"  # ← change me


# ──────────────────────────────────────────────────────────────────────────────
# noun-level help
# ──────────────────────────────────────────────────────────────────────────────

def test_help(runner: CliRunner) -> None:
    res = invoke(runner, NOUN, "--help")
    assert_ok(res)
    assert "Usage:" in res.output


# ──────────────────────────────────────────────────────────────────────────────
# Verb: new
# ──────────────────────────────────────────────────────────────────────────────

class TestNew:
    def test_minimum_args(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.xlsx"
        res = invoke(runner, NOUN, "new", str(out))
        assert_ok(res)
        assert out.exists()

    def test_with_multiple_sheets(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.xlsx"
        invoke(runner, NOUN, "new", str(out), "--sheet", "S1", "--sheet", "S2")
        assert_xlsx_sheets(out, ["S1", "S2"])

    def test_overwrite_without_force_errors(self, runner: CliRunner, tmp_path: Path) -> None:
        out = tmp_path / "x.xlsx"
        out.write_bytes(b"")  # pre-existing
        res = invoke(runner, NOUN, "new", str(out))
        assert res.exit_code != 0


# ──────────────────────────────────────────────────────────────────────────────
# Verb: read
# ──────────────────────────────────────────────────────────────────────────────

class TestRead:
    def test_default_json(self, runner: CliRunner, sample_xlsx) -> None:
        p = sample_xlsx()
        data = assert_json_output(invoke(runner, NOUN, "read", str(p), "--json"))
        assert isinstance(data, list)


# ──────────────────────────────────────────────────────────────────────────────
# Verb: <NEXT VERB> — repeat the pattern
# ──────────────────────────────────────────────────────────────────────────────
