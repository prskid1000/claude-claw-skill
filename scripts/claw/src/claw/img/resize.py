"""claw img resize — Pillow + ImageMagick-geometry resize."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_USAGE, Geometry, common_output_options, die, emit_json, safe_write,
)


@click.command(name="resize")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--geometry", required=True, help="ImageMagick geometry: 100x200, 50%, 100x200!, 100x200>, 100x200^")
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--resample", default=None,
              type=click.Choice(["nearest", "bilinear", "bicubic", "lanczos"], case_sensitive=False),
              help="Override resample filter.")
@click.option("--preserve-icc", is_flag=True, help="Keep ICC profile if present.")
@common_output_options
def resize(src: Path, geometry: str, dst: Path, resample: str | None, preserve_icc: bool,
           force: bool, backup: bool, as_json: bool, dry_run: bool,
           quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Scale an image using ImageMagick geometry."""
    try:
        from PIL import Image
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    try:
        geo = Geometry.parse(geometry)
    except Exception as e:
        die(f"bad --geometry {geometry!r}: {e}", code=EXIT_USAGE, as_json=as_json)

    img = Image.open(src)
    new_w, new_h = geo.apply_to(img.width, img.height)
    shrinking = (new_w * new_h) < (img.width * img.height)

    filter_map = {
        "nearest": Image.NEAREST, "bilinear": Image.BILINEAR,
        "bicubic": Image.BICUBIC, "lanczos": Image.LANCZOS,
    }
    resamp = filter_map[resample.lower()] if resample else (
        Image.LANCZOS if shrinking else Image.BICUBIC)

    if dry_run:
        click.echo(f"would resize {src} {img.width}x{img.height} -> {new_w}x{new_h} -> {dst}")
        return

    out_img = img.resize((max(1, new_w), max(1, new_h)), resamp)

    save_kwargs: dict = {}
    if preserve_icc and "icc_profile" in img.info:
        save_kwargs["icc_profile"] = img.info["icc_profile"]
    if "exif" in img.info:
        save_kwargs["exif"] = img.info["exif"]

    buf = io.BytesIO()
    out_img.save(buf, format=Image.registered_extensions().get(dst.suffix.lower())
                 or img.format or "PNG", **save_kwargs)
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "width": new_w, "height": new_h})
    elif not quiet:
        click.echo(f"wrote {dst} ({new_w}x{new_h})")
