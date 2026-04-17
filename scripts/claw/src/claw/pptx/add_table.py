"""claw pptx add-table — insert a table from CSV / JSON."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_rows, safe_write,
)


@click.command(name="add-table")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--slide", required=True, type=int)
@click.option("--data", "data_src", required=True)
@click.option("--at", "at_pos", default="1in,2in")
@click.option("--size", default="8in,3in")
@click.option("--header", is_flag=True)
@click.option("--widths", default=None)
@common_output_options
def add_table(src: Path, slide: int, data_src: str, at_pos: str, size: str,
              header: bool, widths: str | None,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Insert a native table on a slide from CSV or JSON rows."""
    try:
        from pptx import Presentation
    except ImportError:
        die("python-pptx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[pptx]'", as_json=as_json)

    rows = read_rows(data_src, header=True)
    if not rows:
        die("no data rows", code=EXIT_INPUT, as_json=as_json)

    if isinstance(rows[0], dict):
        headers = list(rows[0].keys())
        grid = [[str(r.get(h, "")) for h in headers] for r in rows]
        if header:
            grid.insert(0, headers)
    else:
        grid = [[str(v) for v in r] for r in rows]

    if dry_run:
        click.echo(f"would add table {len(grid)}x{len(grid[0])} on slide {slide}")
        return

    x, y = [_to_emu(v) for v in at_pos.split(",")]
    w, h = [_to_emu(v) for v in size.split(",")]

    prs = Presentation(str(src))
    target = prs.slides[slide - 1]
    shape = target.shapes.add_table(len(grid), len(grid[0]), x, y, w, h)
    table = shape.table

    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            table.cell(i, j).text = val

    if widths:
        parsed = [_to_emu(w.strip()) for w in widths.split(",")]
        for j, width in enumerate(parsed):
            if j < len(table.columns):
                table.columns[j].width = width

    def _save(f):
        prs.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "slide": slide,
                   "rows": len(grid), "cols": len(grid[0])})
    elif not quiet:
        click.echo(f"added table {len(grid)}x{len(grid[0])} on slide {slide}")


def _to_emu(spec: str):
    from pptx.util import Inches, Cm, Pt, Emu
    spec = spec.strip().lower()
    if spec.endswith("in"):
        return Inches(float(spec[:-2]))
    if spec.endswith("cm"):
        return Cm(float(spec[:-2]))
    if spec.endswith("pt"):
        return Pt(float(spec[:-2]))
    return Emu(int(spec))
