"""claw media concat — join clips (demuxer or re-encode)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, common_output_options, die, emit_json, require, run, safe_copy,
)


@click.command(name="concat")
@click.argument("inputs", nargs=-1, required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--reencode", is_flag=True, help="Force re-encode (normalize codec/size/fps).")
@click.option("--codec", default="h264", type=click.Choice(["h264", "h265", "vp9", "av1"]))
@common_output_options
def concat(inputs: tuple[Path, ...], dst: Path, reencode: bool, codec: str,
           force: bool, backup: bool, as_json: bool, dry_run: bool,
           quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Join multiple clips into one file."""
    try:
        require("ffmpeg")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)

    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp = Path(td) / dst.name
        if reencode:
            codec_map = {"h264": "libx264", "h265": "libx265",
                         "vp9": "libvpx-vp9", "av1": "libaom-av1"}
            filter_parts = []
            inputs_flat: list[str] = []
            for i, p in enumerate(inputs):
                inputs_flat += ["-i", str(p)]
                filter_parts.append(f"[{i}:v:0][{i}:a:0]")
            fc = "".join(filter_parts) + f"concat=n={len(inputs)}:v=1:a=1[v][a]"
            args = ["-y", *inputs_flat, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", codec_map[codec], "-c:a", "aac", str(tmp)]
        else:
            listfile = Path(td) / "list.txt"
            listfile.write_text("".join(f"file '{p.resolve()}'\n" for p in inputs),
                                encoding="utf-8")
            args = ["-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
                    "-c", "copy", str(tmp)]
        if dry_run:
            click.echo("ffmpeg " + " ".join(args))
            return
        try:
            run("ffmpeg", *args)
        except Exception as e:
            die(f"ffmpeg failed (codec/resolution mismatch? try --reencode): {e}",
                code=EXIT_SYSTEM, as_json=as_json)
        safe_copy(tmp, dst, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"inputs": [str(p) for p in inputs], "dst": str(dst),
                   "mode": "reencode" if reencode else "demuxer"})
    elif not quiet:
        click.echo(f"wrote {dst} ({len(inputs)} clips)")
