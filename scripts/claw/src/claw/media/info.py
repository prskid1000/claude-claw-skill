"""claw media info — normalized ffprobe JSON."""

from __future__ import annotations

import json
from pathlib import Path

import click

from claw.common import EXIT_SYSTEM, die, emit_json, require, run


def _utc_key(k: str, v):
    if isinstance(v, str) and "T" in v and (v.endswith("Z") or "+" in v[10:]):
        return {k: v, f"{k}_utc": v}
    return {k: v}


def _normalize_stream(s: dict) -> dict:
    out: dict = {
        "index": s.get("index"),
        "type": s.get("codec_type"),
        "codec": s.get("codec_name"),
    }
    if s.get("codec_type") == "video":
        out["width"] = s.get("width")
        out["height"] = s.get("height")
        fr = s.get("r_frame_rate", "0/1")
        try:
            num, den = fr.split("/")
            out["fps"] = round(float(num) / float(den or 1), 3)
        except Exception:
            out["fps"] = None
    elif s.get("codec_type") == "audio":
        out["channels"] = s.get("channels")
        out["sample_rate"] = int(s["sample_rate"]) if s.get("sample_rate") else None
    br = s.get("bit_rate")
    if br:
        try:
            out["bit_rate"] = int(br)
        except ValueError:
            pass
    return out


def _normalize_format(f: dict) -> dict:
    out: dict = {}
    if f.get("duration"):
        out["duration"] = float(f["duration"])
    if f.get("bit_rate"):
        out["bit_rate"] = int(f["bit_rate"])
    if f.get("size"):
        out["size_bytes"] = int(f["size"])
    if f.get("format_name"):
        out["format_name"] = f["format_name"]
    tags = f.get("tags") or {}
    if "creation_time" in tags:
        out.update(_utc_key("creation_time", tags["creation_time"]))
    return out


@click.command(name="info")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True)
@click.option("--stream", "stream_type", default=None,
              type=click.Choice(["video", "audio", "subtitle"]))
def info(src: Path, as_json: bool, stream_type: str | None) -> None:
    """Inspect streams + format via ffprobe."""
    try:
        require("ffprobe")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)
    r = run("ffprobe", "-v", "error", "-show_format", "-show_streams",
            "-of", "json", str(src))
    raw = json.loads(r.stdout or "{}")
    streams = [_normalize_stream(s) for s in raw.get("streams", [])]
    if stream_type:
        streams = [s for s in streams if s["type"] == stream_type]
    result = {"format": _normalize_format(raw.get("format", {})), "streams": streams}
    if as_json:
        emit_json(result)
        return
    fmt = result["format"]
    click.echo(f"{src}")
    if "duration" in fmt:
        click.echo(f"  duration: {fmt['duration']:.3f} s")
    if "bit_rate" in fmt:
        click.echo(f"  bit_rate: {fmt['bit_rate']} bps")
    if "size_bytes" in fmt:
        click.echo(f"  size:     {fmt['size_bytes']} bytes")
    for s in streams:
        extras = " ".join(f"{k}={v}" for k, v in s.items() if k not in ("index", "type", "codec"))
        click.echo(f"  #{s['index']} {s['type']:8s} {s['codec']:10s} {extras}")
