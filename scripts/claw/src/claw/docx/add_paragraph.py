"""claw docx add-paragraph — append a paragraph with optional formatting."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="add-paragraph")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--text", required=True)
@click.option("--style", "style_name", default=None)
@click.option("--bold", is_flag=True)
@click.option("--italic", is_flag=True)
@click.option("--size", default=None, type=int)
@click.option("--color", default=None)
@click.option("--at", "anchor", default=None)
@click.option("--before/--after", "before", default=False)
@click.option("--align", default=None,
              type=click.Choice(["left", "center", "right", "justify"]))
@common_output_options
def add_paragraph(src: Path, text: str, style_name: str | None,
                  bold: bool, italic: bool, size: int | None, color: str | None,
                  anchor: str | None, before: bool, align: str | None,
                  force: bool, backup: bool, as_json: bool, dry_run: bool,
                  quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Add a paragraph with optional bold/italic/color/size/alignment."""
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Pt, RGBColor
    except ImportError:
        die("python-docx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[docx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would add paragraph: {text[:60]}...")
        return

    doc = Document(str(src))
    new_p = doc.add_paragraph()
    if style_name:
        new_p.style = doc.styles[style_name]
    if align:
        new_p.alignment = getattr(WD_ALIGN_PARAGRAPH, align.upper())
    run = new_p.add_run(text)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if size:
        run.font.size = Pt(size)
    if color:
        hex_c = color.lstrip("#")[:6]
        run.font.color.rgb = RGBColor.from_string(hex_c)

    if anchor:
        target = next((p for p in doc.paragraphs if anchor in p.text and p is not new_p), None)
        if target is None:
            die(f"anchor not found: {anchor!r}", code=EXIT_INPUT, as_json=as_json)
        new_el = new_p._p
        new_el.getparent().remove(new_el)
        if before:
            target._p.addprevious(new_el)
        else:
            target._p.addnext(new_el)

    def _save(f):
        doc.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "added": text[:100]})
    elif not quiet:
        click.echo("added paragraph")
