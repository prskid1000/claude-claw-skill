"""claw img crop — explicit pixel box."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import EXIT_INPUT, EXIT_USAGE, common_output_options, die, emit_json, safe_write


@click.command(name="crop")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--box", required=True, help="x,y,w,h in pixels.")
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@common_output_options
def crop(src: Path, box: str, dst: Path,
         force: bool, backup: bool, as_json: bool, dry_run: bool,
         quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Crop an explicit x,y,w,h pixel box."""
    try:
        from PIL import Image
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    try:
        x, y, w, h = (int(v) for v in box.split(","))
    except Exception as e:
        die(f"bad --box {box!r} (want x,y,w,h): {e}", code=EXIT_USAGE, as_json=as_json)

    if dry_run:
        click.echo(f"would crop {src} box={x},{y},{w},{h} -> {dst}")
        return

    img = Image.open(src)
    out_img = img.crop((x, y, x + w, y + h))
    buf = io.BytesIO()
    out_img.save(buf, format=img.format or "PNG")
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "box": [x, y, w, h]})
    elif not quiet:
        click.echo(f"wrote {dst} ({w}x{h})")
