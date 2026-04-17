"""claw img to-jpeg — alpha-safe JPEG flatten."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="to-jpeg")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--bg", default="white", help="Background color for alpha flatten.")
@click.option("--quality", type=int, default=85)
@click.option("--progressive", is_flag=True)
@common_output_options
def to_jpeg(src: Path, dst: Path, bg: str, quality: int, progressive: bool,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Convert any image to JPEG, flattening alpha onto --bg."""
    try:
        from PIL import Image, ImageColor
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    if dry_run:
        click.echo(f"would flatten {src} onto {bg} -> {dst} q={quality}")
        return

    img = Image.open(src)
    rgba = img.convert("RGBA")
    bg_rgb = ImageColor.getrgb(bg)[:3]
    flat = Image.new("RGB", rgba.size, bg_rgb)
    flat.paste(rgba, mask=rgba.split()[-1])

    kwargs: dict = {"quality": quality, "progressive": progressive}
    if "exif" in img.info:
        kwargs["exif"] = img.info["exif"]
    if "icc_profile" in img.info:
        kwargs["icc_profile"] = img.info["icc_profile"]

    buf = io.BytesIO()
    flat.save(buf, format="JPEG", **kwargs)
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "quality": quality})
    elif not quiet:
        click.echo(f"wrote {dst} (JPEG q={quality})")
