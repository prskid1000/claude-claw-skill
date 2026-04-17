"""claw img watermark — stamp text or logo on a corner."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_USAGE, common_output_options, die, emit_json, safe_write,
)


def _position(pos: str, base: tuple[int, int], overlay: tuple[int, int],
              margin: int) -> tuple[int, int]:
    bw, bh = base
    ow, oh = overlay
    pos = pos.upper()
    vmap = {"T": margin, "C": (bh - oh) // 2, "B": bh - oh - margin}
    hmap = {"L": margin, "C": (bw - ow) // 2, "R": bw - ow - margin}
    if len(pos) != 2 or pos[0] not in vmap or pos[1] not in hmap:
        raise click.UsageError(f"bad --position {pos!r} (use TL|TC|TR|CL|CC|CR|BL|BC|BR)")
    return hmap[pos[1]], vmap[pos[0]]


@click.command(name="watermark")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--text", default=None, help="Text to stamp.")
@click.option("--image", "logo", default=None, type=click.Path(exists=True, path_type=Path),
              help="Logo file.")
@click.option("--position", default="BR", help="TL|TC|TR|CL|CC|CR|BL|BC|BR")
@click.option("--opacity", type=float, default=0.5)
@click.option("--margin", type=int, default=20)
@click.option("--font", "font_path", default=None, type=click.Path(path_type=Path))
@click.option("--size", "font_size", type=int, default=36)
@click.option("--color", default="#ffffff")
@common_output_options
def watermark(src: Path, dst: Path, text: str | None, logo: Path | None, position: str,
              opacity: float, margin: int, font_path: Path | None, font_size: int, color: str,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Stamp text (--text) or a logo (--image) at a corner."""
    try:
        from PIL import Image, ImageColor, ImageDraw, ImageFont
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    if not text and not logo:
        die("one of --text or --image required", code=EXIT_USAGE, as_json=as_json)

    base = Image.open(src).convert("RGBA")

    if logo:
        over = Image.open(logo).convert("RGBA")
    else:
        font = ImageFont.truetype(str(font_path), font_size) if font_path \
            else ImageFont.load_default(size=font_size)
        tmp = Image.new("RGBA", (1, 1))
        bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text or "", font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        over = Image.new("RGBA", (tw + 10, th + 10), (0, 0, 0, 0))
        rgba = ImageColor.getrgb(color)
        if len(rgba) == 3:
            rgba = (*rgba, 255)
        ImageDraw.Draw(over).text((5, 5), text or "", font=font, fill=rgba)

    if opacity < 1.0:
        r, g, b, a = over.split()
        a = a.point(lambda v: int(v * max(0.0, min(1.0, opacity))))
        over = Image.merge("RGBA", (r, g, b, a))

    pos = _position(position, base.size, over.size, margin)

    if dry_run:
        click.echo(f"would watermark {src} pos={position} at={pos} -> {dst}")
        return

    base.alpha_composite(over, pos)
    buf = io.BytesIO()
    base.convert("RGB" if dst.suffix.lower() in (".jpg", ".jpeg") else "RGBA") \
        .save(buf, format=dst.suffix.lstrip(".").upper() or "PNG")
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "position": position, "at": list(pos)})
    elif not quiet:
        click.echo(f"wrote {dst}")
