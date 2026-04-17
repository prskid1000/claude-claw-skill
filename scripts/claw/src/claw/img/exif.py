"""claw img exif — read/strip/auto-rotate."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.group(name="exif", invoke_without_command=True,
             context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
@click.argument("src", required=False, type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True, help="JSON output.")
def exif(ctx: click.Context, src: Path | None, as_json: bool) -> None:
    """EXIF ops: read (default), strip, auto-rotate."""
    if ctx.invoked_subcommand is not None:
        return
    if src is None:
        click.echo(ctx.get_help())
        ctx.exit(2)
    try:
        from PIL import Image, ExifTags
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    img = Image.open(src)
    exif_data = img.getexif()
    out: dict = {}
    for tag_id, value in exif_data.items():
        tag = ExifTags.TAGS.get(tag_id, str(tag_id))
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8", errors="replace")
            except Exception:
                value = repr(value)
        if "DateTime" in tag and isinstance(value, str):
            out[f"{tag}_utc"] = value.replace(":", "-", 2).replace(" ", "T") + "Z"
        out[tag] = value

    if as_json:
        emit_json({"src": str(src), "exif": out})
    else:
        for k, v in out.items():
            click.echo(f"{k}: {v}")


@exif.command(name="strip")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--strip-icc", is_flag=True)
@common_output_options
def strip(src: Path, dst: Path, strip_icc: bool,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Remove EXIF (preserves ICC unless --strip-icc)."""
    from PIL import Image
    if dry_run:
        click.echo(f"would strip exif {src} -> {dst}")
        return
    img = Image.open(src)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    kwargs: dict = {}
    if not strip_icc and "icc_profile" in img.info:
        kwargs["icc_profile"] = img.info["icc_profile"]
    buf = io.BytesIO()
    clean.save(buf, format=img.format or "PNG", **kwargs)
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)
    if not quiet:
        click.echo(f"wrote {dst} (exif stripped)")


@exif.command(name="auto-rotate")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@common_output_options
def auto_rotate(src: Path, dst: Path,
                force: bool, backup: bool, as_json: bool, dry_run: bool,
                quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Bake EXIF orientation into pixels; result has Orientation=1."""
    from PIL import Image, ImageOps
    if dry_run:
        click.echo(f"would auto-rotate {src} -> {dst}")
        return
    img = Image.open(src)
    rotated = ImageOps.exif_transpose(img)
    buf = io.BytesIO()
    rotated.save(buf, format=img.format or "PNG")
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)
    if not quiet:
        click.echo(f"wrote {dst} (auto-rotated)")
