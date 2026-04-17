"""claw media fade — fade-in / fade-out (video + audio)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, common_output_options, die, emit_json, require, run, safe_copy,
)


def _duration(src: Path) -> float:
    r = run("ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(src))
    return float(json.loads(r.stdout or "{}").get("format", {}).get("duration", 0.0))


@click.command(name="fade")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--in", "fade_in", type=float, default=0.0, help="Fade-in seconds.")
@click.option("--out-sec", "fade_out", type=float, default=0.0, help="Fade-out seconds.")
@common_output_options
def fade(src: Path, dst: Path, fade_in: float, fade_out: float,
         force: bool, backup: bool, as_json: bool, dry_run: bool,
         quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Fade in/out for both video and audio."""
    try:
        require("ffmpeg"); require("ffprobe")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)

    dur = _duration(src)
    vf_parts, af_parts = [], []
    if fade_in > 0:
        vf_parts.append(f"fade=t=in:st=0:d={fade_in}")
        af_parts.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out > 0:
        vf_parts.append(f"fade=t=out:st={max(dur - fade_out, 0):.3f}:d={fade_out}")
        af_parts.append(f"afade=t=out:st={max(dur - fade_out, 0):.3f}:d={fade_out}")

    if not vf_parts and not af_parts:
        die("pass at least one of --in / --out-sec", code=2, as_json=as_json)

    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp = Path(td) / dst.name
        args = ["-y", "-i", str(src)]
        if vf_parts:
            args += ["-vf", ",".join(vf_parts)]
        if af_parts:
            args += ["-af", ",".join(af_parts)]
        args.append(str(tmp))
        if dry_run:
            click.echo("ffmpeg " + " ".join(args))
            return
        try:
            run("ffmpeg", *args)
        except Exception as e:
            die(f"ffmpeg failed: {e}", code=EXIT_SYSTEM, as_json=as_json)
        safe_copy(tmp, dst, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst),
                   "fade_in": fade_in, "fade_out": fade_out})
    elif not quiet:
        click.echo(f"wrote {dst}")
