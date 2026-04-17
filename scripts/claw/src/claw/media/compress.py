"""claw media compress — target-size 2-pass or CRF 1-pass."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, EXIT_USAGE, common_output_options, die, emit_json, require, run, safe_copy,
)


def _probe_duration(src: Path) -> float:
    r = run("ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(src))
    return float(json.loads(r.stdout or "{}").get("format", {}).get("duration", 0.0))


def _parse_size(spec: str) -> int:
    s = spec.strip().upper()
    mult = 1
    if s.endswith("K"):
        mult, s = 1024, s[:-1]
    elif s.endswith("M"):
        mult, s = 1024 * 1024, s[:-1]
    elif s.endswith("G"):
        mult, s = 1024 * 1024 * 1024, s[:-1]
    return int(float(s) * mult)


CODEC_MAP = {"h264": "libx264", "h265": "libx265", "vp9": "libvpx-vp9", "av1": "libaom-av1"}


@click.command(name="compress")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--target-size", default=None, help="e.g. 25M, 1.5G.")
@click.option("--crf", type=int, default=None)
@click.option("--codec", default="h264", type=click.Choice(list(CODEC_MAP)))
@click.option("--preset", default="medium")
@click.option("--audio-bitrate", default="128k")
@common_output_options
def compress(src: Path, dst: Path, target_size: str | None, crf: int | None, codec: str,
             preset: str, audio_bitrate: str,
             force: bool, backup: bool, as_json: bool, dry_run: bool,
             quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Shrink video to --target-size (2-pass) or --crf (1-pass)."""
    try:
        require("ffmpeg"); require("ffprobe")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)
    if (target_size is None) == (crf is None):
        die("pass exactly one of --target-size or --crf", code=EXIT_USAGE, as_json=as_json)

    vcodec = CODEC_MAP[codec]

    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp = Path(td) / dst.name

        if crf is not None:
            args = ["-y", "-i", str(src), "-c:v", vcodec, "-crf", str(crf),
                    "-preset", preset, "-c:a", "aac", "-b:a", audio_bitrate, str(tmp)]
            if dry_run:
                click.echo("ffmpeg " + " ".join(args))
                return
            try:
                run("ffmpeg", *args)
            except Exception as e:
                die(f"ffmpeg failed: {e}", code=EXIT_SYSTEM, as_json=as_json)
        else:
            target_bytes = _parse_size(target_size)
            duration = _probe_duration(src)
            audio_bps = int(audio_bitrate.rstrip("kK")) * 1000 if audio_bitrate.endswith(("k", "K")) \
                else int(audio_bitrate)
            total_bps = (target_bytes * 8) / max(duration, 1.0)
            video_bps = max(int(total_bps - audio_bps), 64_000)
            v_kbps = f"{video_bps // 1000}k"
            log = str(Path(td) / "pass")
            null = "NUL"
            pass1 = ["-y", "-i", str(src), "-c:v", vcodec, "-b:v", v_kbps,
                     "-pass", "1", "-passlogfile", log, "-preset", preset,
                     "-an", "-f", "mp4", null]
            pass2 = ["-y", "-i", str(src), "-c:v", vcodec, "-b:v", v_kbps,
                     "-pass", "2", "-passlogfile", log, "-preset", preset,
                     "-c:a", "aac", "-b:a", audio_bitrate, str(tmp)]
            if dry_run:
                click.echo("ffmpeg " + " ".join(pass1))
                click.echo("ffmpeg " + " ".join(pass2))
                return
            try:
                run("ffmpeg", *pass1)
                run("ffmpeg", *pass2)
            except Exception as e:
                die(f"ffmpeg failed: {e}", code=EXIT_SYSTEM, as_json=as_json)

        safe_copy(tmp, dst, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "codec": codec,
                   "mode": "crf" if crf is not None else "target-size"})
    elif not quiet:
        click.echo(f"wrote {dst}")
