"""claw docx read — extract text / structure from a .docx."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, die, emit_json


@click.command(name="read")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--text", "as_text", is_flag=True, help="Plain text (default).")
@click.option("--json", "as_json", is_flag=True, help="Structured JSON.")
@click.option("--tables", "tables_only", is_flag=True, help="Only dump tables.")
@click.option("--headings", "headings_only", is_flag=True, help="Outline of headings.")
@click.option("--style", "style_filter", default=None,
              help="Keep only paragraphs in that style.")
def read(src: Path, as_text: bool, as_json: bool,
         tables_only: bool, headings_only: bool, style_filter: str | None) -> None:
    """Extract text, JSON, tables, or heading outline."""
    try:
        from docx import Document
    except ImportError:
        die("python-docx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[docx]'", as_json=as_json)

    doc = Document(str(src))

    if tables_only:
        all_tables = [[[cell.text for cell in row.cells] for row in t.rows]
                      for t in doc.tables]
        emit_json(all_tables)
        return

    if headings_only:
        for p in doc.paragraphs:
            if p.style.name.startswith("Heading"):
                level = "".join(c for c in p.style.name if c.isdigit()) or "1"
                click.echo(f"{'  ' * (int(level) - 1)}- {p.text}")
        return

    if as_json:
        paragraphs = []
        for p in doc.paragraphs:
            if style_filter and p.style.name != style_filter:
                continue
            paragraphs.append({
                "text": p.text, "style": p.style.name,
                "runs": [{"text": r.text, "bold": r.bold, "italic": r.italic}
                         for r in p.runs],
            })
        tables = [[[c.text for c in row.cells] for row in t.rows] for t in doc.tables]
        emit_json({"paragraphs": paragraphs, "tables": tables})
        return

    for p in doc.paragraphs:
        if style_filter and p.style.name != style_filter:
            continue
        click.echo(p.text)
