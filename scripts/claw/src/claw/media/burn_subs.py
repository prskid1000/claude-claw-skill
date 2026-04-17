"""claw media burn-subs — hardcode subtitles into pixels via libass."""

from __future__ import annotations

import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, common_output_options, die, emit_json, require, run, safe_copy,
)


STYLE_MAP = {
    "FONT": "Fontname", "SIZE": "Fontsize", "COLOR": "PrimaryColour",
    "OUTLINE": "Outline", "SHADOW": "Shadow",
}


def _parse_style(spec: str) -> str:
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    out = []
    for p in parts:
        k, _, v = p.partition("=")
        k = k.strip().upper()
        if k == "BG":
            out.append("BorderStyle=3")
            out.append(f"BackColour={v.strip()}")
        elif k in STYLE_MAP:
            if k == "COLOR" and v.startswith("#"):
                hexv = v.strip().lstrip("#")
                if len(hexv) == 6:
                    r, g, b = hexv[0:2], hexv[2:4], hexv[4:6]
                    v = f"&H00{b}{g}{r}".upper()
            out.append(f"{STYLE_MAP[k]}={v.strip()}")
    return ",".join(out)


@click.command(name="burn-subs")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--srt", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--style", default=None, help="e.g. FONT=Inter,SIZE=26,OUTLINE=2")
@common_output_options
def burn_subs(src: Path, srt: Path, dst: Path, style: str | None,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Hardcode SRT subtitles into the video."""
    try:
        require("ffmpeg")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install Gyan.FFmpeg", as_json=as_json)

    srt_str = str(srt).replace("\\", "/").replace(":", r"\:")
    vf = f"subtitles='{srt_str}'"
    if style:
        vf += f":force_style='{_parse_style(style)}'"

    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp = Path(td) / dst.name
        args = ["-y", "-i", str(src), "-vf", vf, "-c:a", "copy", str(tmp)]
        if dry_run:
            click.echo("ffmpeg " + " ".join(args))
            return
        try:
            run("ffmpeg", *args)
        except Exception as e:
            die(f"ffmpeg failed: {e}", code=EXIT_SYSTEM, as_json=as_json)
        safe_copy(tmp, dst, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "srt": str(srt), "dst": str(dst)})
    elif not quiet:
        click.echo(f"wrote {dst}")
