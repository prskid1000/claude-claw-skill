"""claw pptx add-slide — append a slide with optional title/body/notes."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


@click.command(name="add-slide")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--layout", "layout_idx", default=1, type=int,
              help="0-based index into master's layouts.")
@click.option("--title", default=None)
@click.option("--body", default=None, help="Bullet list or Markdown file path.")
@click.option("--notes", default=None)
@click.option("--at", "at_pos", default="END", help="END or 1-based slide index.")
@common_output_options
def add_slide(src: Path, layout_idx: int, title: str | None, body: str | None,
              notes: str | None, at_pos: str,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Append a slide, optionally pre-populated with title/body/notes."""
    try:
        from pptx import Presentation
    except ImportError:
        die("python-pptx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[pptx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would add slide (layout={layout_idx}, title={title})")
        return

    prs = Presentation(str(src))
    if layout_idx < 0 or layout_idx >= len(prs.slide_layouts):
        die(f"layout {layout_idx} out of range (0..{len(prs.slide_layouts) - 1})",
            code=EXIT_INPUT, as_json=as_json)
    layout = prs.slide_layouts[layout_idx]
    slide = prs.slides.add_slide(layout)

    if title and slide.shapes.title is not None:
        slide.shapes.title.text = title

    if body:
        body_text = body
        body_path = Path(body)
        if body_path.exists() and body_path.is_file():
            body_text = read_text(body)
        body_ph = next((ph for ph in slide.placeholders
                        if ph.placeholder_format.idx != 0
                        and ph.has_text_frame), None)
        if body_ph is not None:
            tf = body_ph.text_frame
            lines = [line.lstrip("- ").rstrip() for line in body_text.splitlines() if line.strip()]
            if lines:
                tf.text = lines[0]
                for extra in lines[1:]:
                    tf.add_paragraph().text = extra

    if notes is not None:
        slide.notes_slide.notes_text_frame.text = notes

    if at_pos != "END" and at_pos.isdigit():
        target = int(at_pos) - 1
        xml_slides = prs.slides._sldIdLst
        slides = list(xml_slides)
        xml_slides.remove(slides[-1])
        xml_slides.insert(target, slides[-1])

    def _save(f):
        prs.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "layout": layout_idx, "title": title})
    elif not quiet:
        click.echo(f"added slide (layout {layout_idx})")
