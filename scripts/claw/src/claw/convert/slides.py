"""claw convert slides — md → reveal.js / beamer / pptx via pandoc."""

from __future__ import annotations

import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, common_output_options, die, emit_json, require, run, safe_copy,
)


FORMAT_MAP = {"reveal": "revealjs", "beamer": "beamer", "pptx": "pptx"}


@click.command(name="slides")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--format", "fmt", required=True, type=click.Choice(list(FORMAT_MAP)))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--theme", default=None)
@click.option("--ref-doc", "ref_doc", default=None, type=click.Path(path_type=Path))
@click.option("--slide-level", type=int, default=2)
@common_output_options
def slides(src: Path, fmt: str, dst: Path, theme: str | None,
           ref_doc: Path | None, slide_level: int,
           force: bool, backup: bool, as_json: bool, dry_run: bool,
           quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Render Markdown slides to reveal.js HTML, Beamer PDF, or PPTX."""
    try:
        require("pandoc")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install JohnMacFarlane.Pandoc", as_json=as_json)

    pandoc_fmt = FORMAT_MAP[fmt]
    args: list[str] = [str(src), "-t", pandoc_fmt, "--standalone",
                       "--slide-level", str(slide_level)]
    if theme:
        if fmt == "reveal":
            args += ["-V", f"theme={theme}"]
        elif fmt == "beamer":
            args += ["-V", f"theme={theme}"]
    if ref_doc and fmt == "pptx":
        args.append(f"--reference-doc={ref_doc}")

    with tempfile.TemporaryDirectory(prefix="claw-") as td:
        tmp = Path(td) / dst.name
        full = [*args, "-o", str(tmp)]
        if dry_run:
            click.echo("pandoc " + " ".join(full))
            return
        try:
            run("pandoc", *full)
        except Exception as e:
            die(f"pandoc failed: {e}", code=EXIT_SYSTEM, as_json=as_json)
        safe_copy(tmp, dst, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"src": str(src), "dst": str(dst), "format": fmt, "theme": theme})
    elif not quiet:
        click.echo(f"wrote {dst} ({pandoc_fmt})")
