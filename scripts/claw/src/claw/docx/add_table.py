"""claw docx add-table — insert a table from CSV / JSON."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_rows, safe_write,
)


@click.command(name="add-table")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--data", "data_src", required=True, help="CSV/JSON file or - for stdin.")
@click.option("--style", "style_name", default="Table Grid")
@click.option("--header", is_flag=True, help="Emit the first row as a header row.")
@click.option("--at", "anchor", default=None)
@click.option("--before/--after", "before", default=False)
@click.option("--widths", default=None, help='Comma-separated widths, e.g. "1in,2in".')
@common_output_options
def add_table(src: Path, data_src: str, style_name: str, header: bool,
              anchor: str | None, before: bool, widths: str | None,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Insert a table in the document from CSV or JSON rows."""
    try:
        from docx import Document
        from docx.shared import Inches
    except ImportError:
        die("python-docx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[docx]'", as_json=as_json)

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
        click.echo(f"would add table: {len(grid)}x{len(grid[0])}")
        return

    doc = Document(str(src))
    table = doc.add_table(rows=len(grid), cols=len(grid[0]))
    try:
        table.style = style_name
    except KeyError:
        pass

    for i, row_data in enumerate(grid):
        for j, val in enumerate(row_data):
            table.cell(i, j).text = val

    if widths:
        parsed = [_parse_width(w.strip()) for w in widths.split(",")]
        for i, w in enumerate(parsed):
            if i < len(table.columns):
                for cell in table.columns[i].cells:
                    cell.width = w

    if anchor:
        target = next((p for p in doc.paragraphs if anchor in p.text), None)
        if target is None:
            die(f"anchor not found: {anchor!r}", code=EXIT_INPUT, as_json=as_json)
        tbl_el = table._tbl
        tbl_el.getparent().remove(tbl_el)
        if before:
            target._p.addprevious(tbl_el)
        else:
            target._p.addnext(tbl_el)

    def _save(f):
        doc.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "rows": len(grid), "cols": len(grid[0])})
    elif not quiet:
        click.echo(f"added table {len(grid)}x{len(grid[0])}")


def _parse_width(spec: str):
    from docx.shared import Inches, Cm, Pt
    if spec.endswith("in"):
        return Inches(float(spec[:-2]))
    if spec.endswith("cm"):
        return Cm(float(spec[:-2]))
    if spec.endswith("pt"):
        return Pt(float(spec[:-2]))
    return Inches(float(spec))
