"""claw media gif — video → GIF via palettegen + paletteuse."""

from __future__ import annotations

import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, common_output_options, die, emit_json, require, run, safe_copy,
)


@click.command(name="gif")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--start", "start_ts", default="0", help="Start time (sec or HH:MM:SS).")
@click.option("--duration", "duration", required=True, help="Duration in seconds.")
@click.option("--width", type=int, default=480)
@click.option("--fps", type=int, default=15)
@click.option("--dither", default="bayer", type=click.Choice(["bayer", "sierra", "none"]))
@common_output_options
def gif(src: Path, dst: Path, start_ts: str, duration: str, width: int, fps: int, dither: str,
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Convert a video slice to an animated GIF."""
    try:
        require("ffmpeg")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)

    base_vf = f"fps={fps},scale={width}:-1:flags=lanczos"
    dither_flag = "none" if dither == "none" else f"bayer:bayer_scale=5" if dither == "bayer" else "sierra2_4a"

    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        palette = Path(td) / "palette.png"
        tmp_out = Path(td) / dst.name

        pass1 = ["-y", "-ss", start_ts, "-t", str(duration), "-i", str(src),
                 "-vf", f"{base_vf},palettegen", str(palette)]
        pass2 = ["-y", "-ss", start_ts, "-t", str(duration), "-i", str(src),
                 "-i", str(palette),
                 "-filter_complex", f"[0:v]{base_vf}[x];[x][1:v]paletteuse=dither={dither_flag}",
                 str(tmp_out)]

        if dry_run:
            click.echo("ffmpeg " + " ".join(pass1))
            click.echo("ffmpeg " + " ".join(pass2))
            return
        try:
            run("ffmpeg", *pass1)
            run("ffmpeg", *pass2)
        except Exception as e:
            die(f"ffmpeg failed: {e}", code=EXIT_SYSTEM, as_json=as_json)
        safe_copy(tmp_out, dst, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "fps": fps, "width": width})
    elif not quiet:
        click.echo(f"wrote {dst}")
