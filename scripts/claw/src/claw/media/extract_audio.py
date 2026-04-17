"""claw media extract-audio — pull audio stream from a video."""

from __future__ import annotations

import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, common_output_options, die, emit_json, require, run, safe_copy,
)


CODEC_MAP = {
    "mp3": ("libmp3lame", "-q:a"),
    "aac": ("aac", "-b:a"),
    "wav": ("pcm_s16le", None),
    "opus": ("libopus", "-b:a"),
    "flac": ("flac", None),
}


@click.command(name="extract-audio")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--format", "fmt", default=None,
              type=click.Choice(list(CODEC_MAP), case_sensitive=False))
@click.option("--quality", type=int, default=None, help="Codec-native quality knob.")
@click.option("--track", type=int, default=0, help="Audio stream index.")
@common_output_options
def extract_audio(src: Path, dst: Path, fmt: str | None, quality: int | None, track: int,
                  force: bool, backup: bool, as_json: bool, dry_run: bool,
                  quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Extract an audio track from video."""
    try:
        require("ffmpeg")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)

    fmt = (fmt or dst.suffix.lstrip(".")).lower()
    if fmt not in CODEC_MAP:
        die(f"unsupported format {fmt!r}", code=2, as_json=as_json)
    codec, qflag = CODEC_MAP[fmt]

    q_args: list[str] = []
    if qflag and quality is not None:
        if fmt == "mp3":
            q_args = [qflag, str(quality)]
        elif fmt in ("aac", "opus"):
            q_args = [qflag, f"{quality}k"]
    elif fmt == "mp3" and quality is None:
        q_args = ["-q:a", "2"]
    elif fmt == "opus" and quality is None:
        q_args = ["-b:a", "96k"]

    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp_out = Path(td) / f"out.{fmt}"
        args = ["-y", "-i", str(src), "-vn", "-map", f"0:a:{track}",
                "-c:a", codec, *q_args, str(tmp_out)]
        if dry_run:
            click.echo("ffmpeg " + " ".join(args))
            return
        try:
            run("ffmpeg", *args)
        except Exception as e:
            die(f"ffmpeg failed: {e}", code=EXIT_SYSTEM, as_json=as_json)
        safe_copy(tmp_out, dst, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "format": fmt, "codec": codec})
    elif not quiet:
        click.echo(f"wrote {dst} ({codec})")
