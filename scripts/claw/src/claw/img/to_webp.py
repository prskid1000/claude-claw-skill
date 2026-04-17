"""claw img to-webp — encode to WebP (lossy/lossless/animated)."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="to-webp")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--quality", type=int, default=85)
@click.option("--lossless", is_flag=True)
@click.option("--animated", is_flag=True, help="For animated GIF source.")
@click.option("--method", type=click.IntRange(0, 6), default=4)
@common_output_options
def to_webp(src: Path, dst: Path, quality: int, lossless: bool, animated: bool, method: int,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Encode to WebP."""
    try:
        from PIL import Image
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    if dry_run:
        click.echo(f"would webp {src} q={quality} lossless={lossless} animated={animated} -> {dst}")
        return

    img = Image.open(src)
    kwargs: dict = {"method": method, "quality": quality, "lossless": lossless}
    if animated and getattr(img, "n_frames", 1) > 1:
        kwargs["save_all"] = True
        frames = []
        durations = []
        for i in range(img.n_frames):
            img.seek(i)
            frames.append(img.convert("RGBA").copy())
            durations.append(img.info.get("duration", 100))
        kwargs["append_images"] = frames[1:]
        kwargs["duration"] = durations
        kwargs["loop"] = img.info.get("loop", 0)
        first = frames[0]
    else:
        first = img

    buf = io.BytesIO()
    first.save(buf, format="WEBP", **kwargs)
    safe_write(dst, lambda f: f.write(buf.getvalue()),
               force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "lossless": lossless, "quality": quality})
    elif not quiet:
        click.echo(f"wrote {dst} (WebP)")
