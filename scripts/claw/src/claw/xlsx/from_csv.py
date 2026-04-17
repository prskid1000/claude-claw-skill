"""claw xlsx from-csv — build a workbook from one or more CSVs."""

from __future__ import annotations

import csv
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="from-csv")
@click.argument("out", type=click.Path(path_type=Path))
@click.argument("csvs", nargs=-1, required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--sheet", "sheet_name", default=None, help="Sheet name (single CSV only).")
@click.option("--delimiter", default=",")
@click.option("--encoding", default="utf-8")
@click.option("--header-row", default=1, type=int, help="1-based row that holds headers.")
@click.option("--types", "types_mode", type=click.Choice(["infer", "text"]), default="infer")
@click.option("--stream", is_flag=True, help="write_only mode for huge sheets.")
@common_output_options
def from_csv(out: Path, csvs: tuple[Path, ...], sheet_name: str | None, delimiter: str,
             encoding: str, header_row: int, types_mode: str, stream: bool,
             force: bool, backup: bool, as_json: bool, dry_run: bool,
             quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Convert one or more CSVs to a workbook (one sheet per CSV)."""
    try:
        from openpyxl import Workbook
    except ImportError:
        die("openpyxl not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[xlsx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would write {out} ({len(csvs)} sheet{'s' if len(csvs) != 1 else ''})")
        return

    wb = Workbook(write_only=stream)
    if not stream:
        wb.remove(wb.active)

    sheets_written = []
    for idx, csv_path in enumerate(csvs):
        name = sheet_name if (sheet_name and len(csvs) == 1) else csv_path.stem
        name = name[:31]
        ws = wb.create_sheet(title=name)
        with open(csv_path, encoding=encoding, newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for i, row in enumerate(reader, start=1):
                if types_mode == "infer" and i >= header_row + 1:
                    row = [_maybe_num(v) for v in row]
                ws.append(row)
        sheets_written.append(name)

    def _save(f):
        wb.save(f)

    safe_write(out, _save, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(out), "sheets": sheets_written})
    elif not quiet:
        click.echo(f"wrote {out} with sheets: {', '.join(sheets_written)}")


def _maybe_num(v: str):
    if v == "" or v is None:
        return v
    try:
        if "." in v or "e" in v.lower():
            return float(v)
        return int(v)
    except (ValueError, AttributeError):
        return v
