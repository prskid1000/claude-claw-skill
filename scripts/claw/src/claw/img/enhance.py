"""claw img enhance — ImageOps chain: autocontrast/equalize/posterize/solarize."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="enhance")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--autocontrast", is_flag=True, help="Stretch histogram.")
@click.option("--cutoff", type=click.IntRange(0, 49), default=0,
              help="Autocontrast cutoff percent.")
@click.option("--equalize", is_flag=True, help="Histogram equalization.")
@click.option("--posterize", type=click.IntRange(1, 8), default=None,
              help="Bits per channel (1-8).")
@click.option("--solarize", type=click.IntRange(0, 255), default=None,
              help="Threshold 0-255 for invert.")
@common_output_options
def enhance(src: Path, dst: Path, autocontrast: bool, cutoff: int, equalize: bool,
            posterize: int | None, solarize: int | None,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Apply tonal corrections (any combination of flags)."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    ops_applied: list[str] = []
    if dry_run:
        if autocontrast: ops_applied.append(f"autocontrast(cutoff={cutoff})")
        if equalize:     ops_applied.append("equalize")
        if posterize:    ops_applied.append(f"posterize({posterize})")
        if solarize is not None: ops_applied.append(f"solarize({solarize})")
        click.echo(f"would enhance {src} ops={ops_applied or ['(none)']} -> {dst}")
        return

    img = Image.open(src)
    working = img.convert("RGB") if img.mode not in ("RGB", "L") else img
    if autocontrast:
        working = ImageOps.autocontrast(working, cutoff=cutoff)
        ops_applied.append(f"autocontrast(cutoff={cutoff})")
    if equalize:
        working = ImageOps.equalize(working)
        ops_applied.append("equalize")
    if posterize:
        working = ImageOps.posterize(working, posterize)
        ops_applied.append(f"posterize({posterize})")
    if solarize is not None:
        working = ImageOps.solarize(working, threshold=solarize)
        ops_applied.append(f"solarize({solarize})")

    buf = io.BytesIO()
    working.save(buf, format=img.format or "PNG")
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "ops": ops_applied})
    elif not quiet:
        click.echo(f"wrote {dst} ({', '.join(ops_applied) or 'no-op'})")
