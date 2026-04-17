"""claw media thumbnail — single frame or contact sheet."""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, EXIT_USAGE, common_output_options, die, emit_json, require, run, safe_write,
)


def _probe_duration(src: Path) -> float:
    r = run("ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(src))
    data = json.loads(r.stdout or "{}")
    return float(data.get("format", {}).get("duration", 0.0))


@click.command(name="thumbnail")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--at", "at_ts", default=None, help="Timestamp of single frame (HH:MM:SS or seconds).")
@click.option("--count", type=int, default=None, help="Total frames for contact sheet.")
@click.option("--grid", default=None, help="WxH (e.g. 4x4) — required with --count.")
@click.option("--width", type=int, default=None, help="Per-frame width; height auto.")
@common_output_options
def thumbnail(src: Path, dst: Path, at_ts: str | None, count: int | None, grid: str | None,
              width: int | None,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Grab one still (--at) or a contact sheet (--count --grid)."""
    try:
        require("ffmpeg"); require("ffprobe")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)

    if at_ts is None and count is None:
        die("pass --at or --count+--grid", code=EXIT_USAGE, as_json=as_json)

    vf = f"scale={width}:-1" if width else None

    if at_ts is not None:
        args = ["-y", "-ss", str(at_ts), "-i", str(src), "-frames:v", "1"]
        if vf:
            args += ["-vf", vf]
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
            data = tmp.read_bytes()
        safe_write(dst, lambda f: f.write(data), force=force, backup=backup, mkdir=mkdir)
        if as_json:
            emit_json({"src": str(src), "dst": str(dst), "at": at_ts})
        elif not quiet:
            click.echo(f"wrote {dst}")
        return

    if not grid:
        die("--grid WxH required with --count", code=EXIT_USAGE, as_json=as_json)
    cols, rows = (int(x) for x in grid.lower().split("x", 1))
    if cols * rows != count:
        die(f"--count {count} must equal cols*rows ({cols*rows})", code=EXIT_USAGE, as_json=as_json)

    duration = _probe_duration(src)
    step = max(duration / count, 0.01)

    scale_expr = f",scale={width}:-1" if width else ""
    vf_expr = f"fps=1/{step}{scale_expr},tile={cols}x{rows}"

    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp = Path(td) / dst.name
        args = ["-y", "-i", str(src), "-vf", vf_expr, "-frames:v", "1", str(tmp)]
        if dry_run:
            click.echo("ffmpeg " + " ".join(args))
            return
        try:
            run("ffmpeg", *args)
        except Exception as e:
            die(f"ffmpeg failed: {e}", code=EXIT_SYSTEM, as_json=as_json)
        data = tmp.read_bytes()
    safe_write(dst, lambda f: f.write(data), force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "count": count, "grid": grid})
    elif not quiet:
        click.echo(f"wrote {dst} ({cols}x{rows} grid)")
