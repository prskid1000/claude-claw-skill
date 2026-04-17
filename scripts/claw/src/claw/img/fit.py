"""claw img fit — crop-to-fill via PIL.ImageOps.fit."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_USAGE, common_output_options, die, emit_json, safe_write,
)


def _parse_size(spec: str) -> tuple[int, int]:
    w, h = spec.lower().split("x", 1)
    return int(w), int(h)


def _parse_center(spec: str) -> tuple[float, float]:
    x, y = spec.split(",", 1)
    return float(x), float(y)


@click.command(name="fit")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--size", required=True, help="WxH in pixels (e.g. 400x400).")
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--center", default="0.5,0.5", help="X,Y bias 0..1 (e.g. 0.5,0.3).")
@click.option("--resample", default="lanczos",
              type=click.Choice(["nearest", "bilinear", "bicubic", "lanczos"], case_sensitive=False))
@common_output_options
def fit(src: Path, size: str, dst: Path, center: str, resample: str,
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Scale + crop so both dims exactly match --size."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    try:
        w, h = _parse_size(size)
        cx, cy = _parse_center(center)
    except Exception as e:
        die(f"bad --size/--center: {e}", code=EXIT_USAGE, as_json=as_json)

    filt = {"nearest": Image.NEAREST, "bilinear": Image.BILINEAR,
            "bicubic": Image.BICUBIC, "lanczos": Image.LANCZOS}[resample.lower()]

    if dry_run:
        click.echo(f"would fit {src} -> {w}x{h} centering={cx},{cy} -> {dst}")
        return

    img = Image.open(src)
    out_img = ImageOps.fit(img, (w, h), method=filt, centering=(cx, cy))
    buf = io.BytesIO()
    out_img.save(buf, format=img.format or "PNG")
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "width": w, "height": h})
    elif not quiet:
        click.echo(f"wrote {dst} ({w}x{h})")
