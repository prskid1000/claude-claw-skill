"""claw img convert — extension-dispatched format translation."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


EXT_TO_PIL = {
    ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP",
    ".gif": "GIF", ".tiff": "TIFF", ".tif": "TIFF", ".bmp": "BMP",
    ".ico": "ICO", ".pdf": "PDF",
}


@click.command(name="convert")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.argument("dst", type=click.Path(path_type=Path))
@click.option("--quality", type=int, default=None)
@click.option("--lossless", is_flag=True)
@click.option("--strip-exif", is_flag=True)
@click.option("--preserve-icc", is_flag=True)
@common_output_options
def convert_(src: Path, dst: Path, quality: int | None, lossless: bool, strip_exif: bool,
             preserve_icc: bool,
             force: bool, backup: bool, as_json: bool, dry_run: bool,
             quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Convert an image to a new format based on the output extension."""
    try:
        from PIL import Image
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    ext = dst.suffix.lower()
    pil_fmt = EXT_TO_PIL.get(ext)
    if pil_fmt is None:
        die(f"unsupported output extension {ext!r}", code=2, as_json=as_json)

    if dry_run:
        click.echo(f"would convert {src} -> {dst} ({pil_fmt})")
        return

    img = Image.open(src)
    if pil_fmt == "JPEG" and img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        rgba = img.convert("RGBA")
        bg.paste(rgba, mask=rgba.split()[-1])
        img = bg
        sys.stderr.write("warning: flattened alpha onto white for JPEG output\n")

    kwargs: dict = {}
    if quality is not None:
        kwargs["quality"] = quality
    if lossless and pil_fmt == "WEBP":
        kwargs["lossless"] = True
    if not strip_exif and "exif" in img.info:
        kwargs["exif"] = img.info["exif"]
    if preserve_icc and "icc_profile" in img.info:
        kwargs["icc_profile"] = img.info["icc_profile"]

    buf = io.BytesIO()
    img.save(buf, format=pil_fmt, **kwargs)
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "format": pil_fmt})
    elif not quiet:
        click.echo(f"wrote {dst} ({pil_fmt})")
