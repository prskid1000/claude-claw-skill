"""claw docx add-heading — append or insert a heading."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="add-heading")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--text", required=True)
@click.option("--level", default=1, type=click.IntRange(1, 9))
@click.option("--at", "anchor", default=None, help="Insert near this anchor text.")
@click.option("--before/--after", "before", default=False)
@click.option("--style", "style_name", default=None)
@common_output_options
def add_heading(src: Path, text: str, level: int, anchor: str | None,
                before: bool, style_name: str | None,
                force: bool, backup: bool, as_json: bool, dry_run: bool,
                quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Append a heading or insert one at an anchor paragraph."""
    try:
        from docx import Document
    except ImportError:
        die("python-docx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[docx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would add heading (level={level}): {text}")
        return

    doc = Document(str(src))

    if anchor:
        target = next((p for p in doc.paragraphs if anchor in p.text), None)
        if target is None:
            die(f"anchor not found: {anchor!r}", code=EXIT_INPUT, as_json=as_json)
        new_p = doc.add_heading(text, level=level)
        if style_name:
            new_p.style = doc.styles[style_name]
        target_el = target._p
        new_el = new_p._p
        new_el.getparent().remove(new_el)
        if before:
            target_el.addprevious(new_el)
        else:
            target_el.addnext(new_el)
    else:
        p = doc.add_heading(text, level=level)
        if style_name:
            p.style = doc.styles[style_name]

    def _save(f):
        doc.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "text": text, "level": level})
    elif not quiet:
        click.echo(f"added heading: {text}")
