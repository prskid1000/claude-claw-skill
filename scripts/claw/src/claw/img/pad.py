"""claw img pad — letterbox to target canvas."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="pad")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--size", required=True, help="WxH target canvas.")
@click.option("--color", default="black", help="Fill color (name or #RRGGBB[AA]).")
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@common_output_options
def pad(src: Path, size: str, color: str, dst: Path,
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Letterbox: image preserved max-size, remainder filled with --color."""
    try:
        from PIL import Image, ImageColor, ImageOps
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    w, h = (int(x) for x in size.lower().split("x", 1))
    try:
        fill = ImageColor.getrgb(color)
    except ValueError as e:
        die(f"bad --color {color!r}: {e}", code=2, as_json=as_json)

    if dry_run:
        click.echo(f"would pad {src} -> {w}x{h} color={color} -> {dst}")
        return

    img = Image.open(src)
    out_img = ImageOps.pad(img, (w, h), method=Image.LANCZOS, color=fill, centering=(0.5, 0.5))
    buf = io.BytesIO()
    out_img.save(buf, format=img.format or "PNG")
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "width": w, "height": h})
    elif not quiet:
        click.echo(f"wrote {dst} ({w}x{h})")
