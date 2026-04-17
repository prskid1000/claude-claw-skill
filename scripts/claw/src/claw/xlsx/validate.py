"""claw xlsx validate — add a data-validation rule to a range."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="validate")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--sheet", required=True)
@click.option("--range", "a1_range", required=True)
@click.option("--type", "kind", required=True,
              type=click.Choice(["list", "whole", "decimal", "date", "time",
                                 "textLength", "custom"]))
@click.option("--values", default=None, help="Comma-separated list (for --type list).")
@click.option("--source", default=None, help="Cell-range reference (for --type list).")
@click.option("--operator", default=None,
              type=click.Choice(["between", "notBetween", "equal", "notEqual",
                                 "greaterThan", "lessThan",
                                 "greaterThanOrEqual", "lessThanOrEqual"]))
@click.option("--formula1", default=None)
@click.option("--formula2", default=None)
@click.option("--error-style", "error_style", default="stop",
              type=click.Choice(["stop", "warning", "information"]))
@click.option("--prompt", default=None)
@common_output_options
def validate(src: Path, sheet: str, a1_range: str, kind: str,
             values: str | None, source: str | None, operator: str | None,
             formula1: str | None, formula2: str | None,
             error_style: str, prompt: str | None,
             force: bool, backup: bool, as_json: bool, dry_run: bool,
             quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Add a list / whole / decimal / date / time / textLength / custom rule."""
    try:
        from openpyxl import load_workbook
        from openpyxl.worksheet.datavalidation import DataValidation
    except ImportError:
        die("openpyxl not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[xlsx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would add {kind} validation on {sheet}!{a1_range}")
        return

    wb = load_workbook(src)
    ws = wb[sheet]

    f1 = formula1
    if kind == "list":
        if values:
            f1 = '"' + values + '"'
        elif source:
            f1 = source
        else:
            die("--values or --source required for --type list",
                code=EXIT_INPUT, as_json=as_json)

    dv = DataValidation(type=kind, formula1=f1, formula2=formula2,
                        operator=operator, errorStyle=error_style,
                        prompt=prompt or "")
    dv.add(a1_range)
    ws.add_data_validation(dv)

    def _save(f):
        wb.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "sheet": sheet, "range": a1_range, "type": kind})
    elif not quiet:
        click.echo(f"added {kind} validation on {sheet}!{a1_range}")
