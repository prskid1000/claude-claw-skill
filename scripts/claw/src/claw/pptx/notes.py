"""claw pptx notes — set speaker notes on a slide."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


@click.command(name="notes")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--slide", required=True, type=int)
@click.option("--text", default=None, help="Literal text or path to a .md file.")
@click.option("--append", is_flag=True)
@click.option("--clear", is_flag=True)
@common_output_options
def notes(src: Path, slide: int, text: str | None, append: bool, clear: bool,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Set / append / clear speaker notes on a slide."""
    try:
        from pptx import Presentation
    except ImportError:
        die("python-pptx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[pptx]'", as_json=as_json)

    if not clear and text is None:
        die("--text required unless --clear", code=EXIT_INPUT, as_json=as_json)

    body = ""
    if text is not None:
        body_path = Path(text)
        body = read_text(text) if (body_path.exists() and body_path.is_file()) else text

    if dry_run:
        action = "clear" if clear else ("append" if append else "set")
        click.echo(f"would {action} notes on slide {slide}")
        return

    prs = Presentation(str(src))
    target = prs.slides[slide - 1]
    tf = target.notes_slide.notes_text_frame
    if clear:
        tf.text = ""
    elif append:
        existing = tf.text or ""
        tf.text = existing + ("\n" if existing else "") + body
    else:
        tf.text = body

    def _save(f):
        prs.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "slide": slide, "cleared": clear,
                   "appended": append, "length": len(body)})
    elif not quiet:
        click.echo(f"{'cleared' if clear else 'set'} notes on slide {slide}")
