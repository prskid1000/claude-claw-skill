"""claw img composite — alpha-correct paste of --fg on --bg at --at."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_USAGE, common_output_options, die, emit_json, safe_write,
)


def _load_bg(spec: str, size_hint: tuple[int, int] | None):
    from PIL import Image, ImageColor
    p = Path(spec)
    if p.exists():
        return Image.open(p).convert("RGBA")
    try:
        rgba = ImageColor.getrgb(spec)
    except ValueError as e:
        raise click.UsageError(f"--bg {spec!r}: not a file and not a color ({e})")
    if rgba is not None and len(rgba) == 3:
        rgba = (*rgba, 255)
    if size_hint is None:
        raise click.UsageError("--bg color requires an --fg image to define canvas size")
    return Image.new("RGBA", size_hint, rgba)


@click.command(name="composite")
@click.option("--bg", required=True, help="Background: path or color.")
@click.option("--fg", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--at", "at_spec", default="0,0", help="Foreground offset x,y.")
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--alpha", type=float, default=1.0, help="Multiply fg alpha (0-1).")
@common_output_options
def composite(bg: str, fg: Path, at_spec: str, dst: Path, alpha: float,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Alpha-composite fg onto bg at x,y."""
    try:
        from PIL import Image
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    try:
        x, y = (int(v) for v in at_spec.split(","))
    except Exception as e:
        die(f"bad --at {at_spec!r}: {e}", code=EXIT_USAGE, as_json=as_json)

    fg_img = Image.open(fg).convert("RGBA")
    bg_img = _load_bg(bg, size_hint=fg_img.size)

    if alpha != 1.0:
        r, g, b, a = fg_img.split()
        a = a.point(lambda v: int(v * max(0.0, min(1.0, alpha))))
        fg_img = Image.merge("RGBA", (r, g, b, a))

    if dry_run:
        click.echo(f"would composite fg={fg} on bg={bg} at={x},{y} -> {dst}")
        return

    canvas = Image.new("RGBA", bg_img.size)
    canvas.alpha_composite(bg_img, (0, 0))
    canvas.alpha_composite(fg_img, (x, y))

    buf = io.BytesIO()
    canvas.save(buf, format=dst.suffix.lstrip(".").upper() or "PNG")
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"dst": str(dst), "size": list(canvas.size)})
    elif not quiet:
        click.echo(f"wrote {dst} ({canvas.width}x{canvas.height})")
