"""claw img thumb — fast downscale with EXIF-aware rotation."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="thumb")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--max", "max_side", required=True, type=int, help="Longest edge in pixels.")
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--format", "fmt", default=None,
              type=click.Choice(["jpeg", "webp", "png"], case_sensitive=False))
@common_output_options
def thumb(src: Path, max_side: int, dst: Path, fmt: str | None,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Fast thumbnail: exif_transpose + Image.thumbnail."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    if dry_run:
        click.echo(f"would thumb {src} --max {max_side} -> {dst}")
        return

    img = Image.open(src)
    if img.format == "JPEG":
        try:
            img.draft("RGB", (max_side, max_side))
        except Exception:
            pass
    img = ImageOps.exif_transpose(img)

    before = img.size
    out_img = img.copy()
    out_img.thumbnail((max_side, max_side), Image.LANCZOS, reducing_gap=3.0)
    did_work = out_img.size != before

    pil_fmt = (fmt or dst.suffix.lstrip(".")).upper()
    if pil_fmt == "JPG":
        pil_fmt = "JPEG"
    buf = io.BytesIO()
    out_img.save(buf, format=pil_fmt)
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst),
                   "width": out_img.width, "height": out_img.height,
                   "resized": did_work})
    elif not quiet:
        msg = f"wrote {dst} ({out_img.width}x{out_img.height})"
        if not did_work:
            msg += " [already ≤ max — copy]"
        click.echo(msg)
