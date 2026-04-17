"""claw media scale — resize video via -vf scale=."""

from __future__ import annotations

import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, Geometry, common_output_options, die, emit_json, require, run, safe_copy,
)


@click.command(name="scale")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--geometry", required=True, help="ImageMagick geometry.")
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--codec", default="h264", type=click.Choice(["h264", "h265", "vp9", "av1"]))
@click.option("--crf", type=int, default=20)
@common_output_options
def scale(src: Path, geometry: str, dst: Path, codec: str, crf: int,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Scale a video to a target geometry."""
    try:
        require("ffmpeg")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)

    geo = Geometry.parse(geometry)
    if geo.pct is not None:
        vf = f"scale=iw*{geo.pct/100}:ih*{geo.pct/100}"
    else:
        w = geo.width if geo.width is not None else -1
        h = geo.height if geo.height is not None else -1
        flags = ":force_original_aspect_ratio=disable" if geo.force else ""
        vf = f"scale={w}:{h}{flags}"

    codec_map = {"h264": "libx264", "h265": "libx265", "vp9": "libvpx-vp9", "av1": "libaom-av1"}
    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp = Path(td) / dst.name
        args = ["-y", "-i", str(src), "-vf", vf, "-c:v", codec_map[codec],
                "-crf", str(crf), "-c:a", "copy", str(tmp)]
        if dry_run:
            click.echo("ffmpeg " + " ".join(args))
            return
        try:
            run("ffmpeg", *args)
        except Exception as e:
            die(f"ffmpeg failed: {e}", code=EXIT_SYSTEM, as_json=as_json)
        safe_copy(tmp, dst, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "vf": vf})
    elif not quiet:
        click.echo(f"wrote {dst}")
