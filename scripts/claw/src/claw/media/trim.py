"""claw media trim — cut a time range (stream-copy or precise re-encode)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, common_output_options, die, emit_json, require, run, safe_copy,
)


def _to_seconds(ts: str) -> float:
    if ":" not in ts:
        return float(ts)
    parts = [float(p) for p in ts.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


@click.command(name="trim")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--from", "t_from", required=True, help="Start (HH:MM:SS or seconds).")
@click.option("--to", "t_to", required=True, help="End (HH:MM:SS or seconds).")
@click.option("--precise", is_flag=True, help="Re-encode for exact cut points.")
@click.option("--codec", default="h264", help="Codec for --precise mode.")
@common_output_options
def trim(src: Path, dst: Path, t_from: str, t_to: str, precise: bool, codec: str,
         force: bool, backup: bool, as_json: bool, dry_run: bool,
         quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Cut [t_from, t_to] from a video."""
    try:
        require("ffmpeg")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)

    duration = _to_seconds(t_to) - _to_seconds(t_from)
    if duration <= 0:
        die("--to must be after --from", code=2, as_json=as_json)

    codec_map = {"h264": "libx264", "h265": "libx265", "vp9": "libvpx-vp9", "av1": "libaom-av1"}
    vcodec = codec_map.get(codec, codec)

    if precise:
        args = ["-y", "-ss", t_from, "-i", str(src), "-t", str(duration),
                "-c:v", vcodec, "-c:a", "aac", "-preset", "medium"]
    else:
        args = ["-y", "-ss", t_from, "-i", str(src), "-t", str(duration), "-c", "copy"]

    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp = Path(td) / dst.name
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
                   "from": t_from, "to": t_to, "precise": precise})
    elif not quiet:
        click.echo(f"wrote {dst} ({'precise' if precise else 'stream-copy'})")
