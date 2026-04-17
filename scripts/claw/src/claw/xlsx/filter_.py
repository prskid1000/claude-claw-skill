"""claw xlsx filter — toggle auto-filter on a range."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="filter")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--sheet", required=True)
@click.option("--range", "a1_range", default=None, help="A1 range; default = sheet dimensions.")
@click.option("--off", is_flag=True, help="Remove auto-filter instead.")
@common_output_options
def filter_(src: Path, sheet: str, a1_range: str | None, off: bool,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Turn auto-filter on (or --off) for a range."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        die("openpyxl not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[xlsx]'", as_json=as_json)

    if dry_run:
        action = "off" if off else (a1_range or "auto")
        click.echo(f"would set auto-filter={action} on {sheet}")
        return

    wb = load_workbook(src)
    ws = wb[sheet]
    if off:
        ws.auto_filter.ref = None
        rng = None
    else:
        rng = a1_range or ws.dimensions
        ws.auto_filter.ref = rng

    def _save(f):
        wb.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "sheet": sheet, "filter": rng})
    elif not quiet:
        click.echo(f"{'removed' if off else 'set'} auto-filter on {sheet} ({rng or ''})")
