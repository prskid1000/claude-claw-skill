"""claw xlsx new — create a blank .xlsx."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="new")
@click.argument("out", type=click.Path(path_type=Path))
@click.option("--sheet", "sheets", multiple=True, help="Sheet name(s); repeat for multiple.")
@common_output_options
def new(out: Path, sheets: tuple[str, ...],
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Create a blank .xlsx workbook with one or more named sheets."""
    try:
        from openpyxl import Workbook
    except ImportError:
        die("openpyxl not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[xlsx]'", as_json=as_json)

    sheet_names = list(sheets) or ["Sheet1"]

    if dry_run:
        click.echo(f"would write {out} with sheets: {', '.join(sheet_names)}")
        return

    wb = Workbook()
    default = wb.active
    default.title = sheet_names[0]
    for name in sheet_names[1:]:
        wb.create_sheet(title=name)

    def _save(f):
        wb.save(f)

    safe_write(out, _save, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(out), "sheets": sheet_names})
    elif not quiet:
        click.echo(f"wrote {out} ({len(sheet_names)} sheet{'s' if len(sheet_names) != 1 else ''})")
