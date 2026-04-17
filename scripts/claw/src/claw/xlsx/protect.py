"""claw xlsx protect — password-protect a sheet or the workbook structure."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


ALLOWABLE = {
    "select-locked": "selectLockedCells", "select-unlocked": "selectUnlockedCells",
    "format-cells": "formatCells", "format-columns": "formatColumns",
    "format-rows": "formatRows", "insert-columns": "insertColumns",
    "insert-rows": "insertRows", "insert-hyperlinks": "insertHyperlinks",
    "delete-columns": "deleteColumns", "delete-rows": "deleteRows",
    "sort": "sort", "auto-filter": "autoFilter", "pivot-tables": "pivotTables",
    "objects": "objects", "scenarios": "scenarios",
}


@click.command(name="protect")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--scope", required=True, type=click.Choice(["sheet", "workbook"]))
@click.option("--sheet", default=None)
@click.option("--password", default=None)
@click.option("--allow", default="", help="Comma-separated actions to permit.")
@click.option("--clear", is_flag=True, help="Remove protection instead of applying it.")
@common_output_options
def protect(src: Path, scope: str, sheet: str | None, password: str | None,
            allow: str, clear: bool,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Apply or clear sheet/workbook password protection."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        die("openpyxl not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[xlsx]'", as_json=as_json)

    if not clear and not password:
        die("--password required unless --clear is given",
            code=EXIT_INPUT, as_json=as_json)

    if dry_run:
        click.echo(f"would {'clear' if clear else 'apply'} {scope} protection on {src}")
        return

    wb = load_workbook(src)
    allowed = {ALLOWABLE[a.strip()] for a in allow.split(",") if a.strip() in ALLOWABLE}

    if scope == "sheet":
        if not sheet:
            die("--sheet required for --scope sheet", code=EXIT_INPUT, as_json=as_json)
        ws = wb[sheet]
        if clear:
            ws.protection.sheet = False
            ws.protection.password = None
        else:
            ws.protection.sheet = True
            ws.protection.password = password
            for key in ALLOWABLE.values():
                if hasattr(ws.protection, key):
                    setattr(ws.protection, key, key in allowed)
    else:
        if clear:
            wb.security = None
        else:
            wb.security = wb.security or type("S", (), {})()
            wb.security.workbookPassword = password
            wb.security.lockStructure = True

    def _save(f):
        wb.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "scope": scope,
                   "cleared": clear, "sheet": sheet})
    elif not quiet:
        click.echo(f"{'cleared' if clear else 'applied'} {scope} protection")
