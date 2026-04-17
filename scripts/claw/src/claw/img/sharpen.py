"""claw img sharpen — unsharp mask."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="sharpen")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--radius", type=float, default=2.0, help="Blur radius (px).")
@click.option("--amount", type=int, default=150, help="Sharpen percent.")
@click.option("--threshold", type=int, default=3, help="Skip pixels below this contrast.")
@common_output_options
def sharpen(src: Path, dst: Path, radius: float, amount: int, threshold: int,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Apply an unsharp mask."""
    try:
        from PIL import Image, ImageFilter
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    if dry_run:
        click.echo(f"would sharpen {src} r={radius} a={amount} t={threshold} -> {dst}")
        return

    img = Image.open(src)
    out_img = img.filter(ImageFilter.UnsharpMask(radius=radius, percent=amount, threshold=threshold))
    buf = io.BytesIO()
    out_img.save(buf, format=img.format or "PNG")
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst),
                   "radius": radius, "amount": amount, "threshold": threshold})
    elif not quiet:
        click.echo(f"wrote {dst}")
