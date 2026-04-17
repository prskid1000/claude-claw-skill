"""claw docx add-image — insert an inline image."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="add-image")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--image", "image_path", required=True,
              type=click.Path(exists=True, path_type=Path))
@click.option("--width", default=None, type=float, help="Inches.")
@click.option("--height", default=None, type=float, help="Inches.")
@click.option("--at", "anchor", default=None)
@click.option("--before/--after", "before", default=False)
@click.option("--align", default=None,
              type=click.Choice(["left", "center", "right"]))
@common_output_options
def add_image(src: Path, image_path: Path, width: float | None, height: float | None,
              anchor: str | None, before: bool, align: str | None,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Insert an inline image (optionally at an anchor paragraph)."""
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Inches
    except ImportError:
        die("python-docx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[docx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would insert {image_path}")
        return

    doc = Document(str(src))
    p = doc.add_paragraph()
    if align:
        p.alignment = getattr(WD_ALIGN_PARAGRAPH, align.upper())
    run = p.add_run()
    kwargs = {}
    if width:
        kwargs["width"] = Inches(width)
    if height:
        kwargs["height"] = Inches(height)
    run.add_picture(str(image_path), **kwargs)

    if anchor:
        target = next((para for para in doc.paragraphs if anchor in para.text and para is not p), None)
        if target is None:
            die(f"anchor not found: {anchor!r}", code=EXIT_INPUT, as_json=as_json)
        new_el = p._p
        new_el.getparent().remove(new_el)
        if before:
            target._p.addprevious(new_el)
        else:
            target._p.addnext(new_el)

    def _save(f):
        doc.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "image": str(image_path)})
    elif not quiet:
        click.echo(f"inserted {image_path}")
