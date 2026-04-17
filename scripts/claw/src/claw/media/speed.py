"""claw media speed — change playback speed; chains atempo for |F| outside [0.5, 2]."""

from __future__ import annotations

import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, common_output_options, die, emit_json, require, run, safe_copy,
)


def _atempo_chain(factor: float) -> str:
    parts: list[str] = []
    remaining = factor
    while remaining > 2.0:
        parts.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        parts.append("atempo=0.5")
        remaining /= 0.5
    parts.append(f"atempo={remaining:.6f}")
    return ",".join(parts)


@click.command(name="speed")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--factor", type=float, required=True)
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--no-audio", is_flag=True)
@common_output_options
def speed(src: Path, factor: float, dst: Path, no_audio: bool,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Change video playback speed by --factor."""
    try:
        require("ffmpeg")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)
    if factor <= 0:
        die("--factor must be > 0", code=2, as_json=as_json)

    v_pts = 1.0 / factor
    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp = Path(td) / dst.name
        if no_audio:
            args = ["-y", "-i", str(src), "-filter:v", f"setpts={v_pts}*PTS",
                    "-an", str(tmp)]
        else:
            atempo = _atempo_chain(factor)
            fc = f"[0:v]setpts={v_pts}*PTS[v];[0:a]{atempo}[a]"
            args = ["-y", "-i", str(src), "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", str(tmp)]
        if dry_run:
            click.echo("ffmpeg " + " ".join(args))
            return
        try:
            run("ffmpeg", *args)
        except Exception as e:
            die(f"ffmpeg failed: {e}", code=EXIT_SYSTEM, as_json=as_json)
        safe_copy(tmp, dst, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "factor": factor})
    elif not quiet:
        click.echo(f"wrote {dst} ({factor}x)")
