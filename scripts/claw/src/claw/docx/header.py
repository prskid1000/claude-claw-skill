"""claw docx header — set header text on a section."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="header")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--text", required=True)
@click.option("--section", default=None, type=int,
              help="1-based section index; default = all sections.")
@click.option("--align", default=None,
              type=click.Choice(["left", "center", "right"]))
@click.option("--type", "header_type", default="primary",
              type=click.Choice(["primary", "first-page", "even-page"]))
@common_output_options
def header(src: Path, text: str, section: int | None, align: str | None,
           header_type: str,
           force: bool, backup: bool, as_json: bool, dry_run: bool,
           quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Set the header text for a section (default = all sections)."""
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        die("python-docx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[docx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would set header: {text}")
        return

    doc = Document(str(src))
    sections = [doc.sections[section - 1]] if section else list(doc.sections)

    for sec in sections:
        if header_type == "first-page":
            sec.different_first_page_header_footer = True
            h = sec.first_page_header
        elif header_type == "even-page":
            h = sec.even_page_header
        else:
            h = sec.header
        p = h.paragraphs[0] if h.paragraphs else h.add_paragraph()
        p.text = text
        if align:
            p.alignment = getattr(WD_ALIGN_PARAGRAPH, align.upper())

    def _save(f):
        doc.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "header": text,
                   "sections": [s.start_type for s in sections]})
    elif not quiet:
        click.echo(f"set header on {len(sections)} section(s)")
