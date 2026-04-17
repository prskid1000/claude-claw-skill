"""claw convert book — concatenate chapters into a single output."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import click

from claw.common import (
    EXIT_SYSTEM, common_output_options, die, emit_json, require, run, safe_copy,
)


@click.command(name="book")
@click.argument("chapters", nargs=-1, required=True,
                type=click.Path(exists=True, path_type=Path))
@click.option("--out", "dst", required=True, type=click.Path(path_type=Path))
@click.option("--title", default=None)
@click.option("--author", default=None)
@click.option("--metadata", multiple=True)
@click.option("--toc", is_flag=True)
@click.option("--toc-depth", type=int, default=None)
@click.option("--csl", default=None, type=click.Path(path_type=Path))
@click.option("--bib", default=None, type=click.Path(path_type=Path))
@click.option("--css", default=None, type=click.Path(path_type=Path))
@click.option("--engine", default=None)
@click.option("--ref-doc", "ref_doc", default=None, type=click.Path(path_type=Path))
@click.option("--cover", default=None, type=click.Path(path_type=Path))
@click.option("--stream", "stream_progress", is_flag=True)
@common_output_options
def book(chapters: tuple[Path, ...], dst: Path, title: str | None, author: str | None,
         metadata: tuple[str, ...], toc: bool, toc_depth: int | None,
         csl: Path | None, bib: Path | None, css: Path | None, engine: str | None,
         ref_doc: Path | None, cover: Path | None, stream_progress: bool,
         force: bool, backup: bool, as_json: bool, dry_run: bool,
         quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Concatenate chapters into a single pdf/epub/docx/html."""
    try:
        require("pandoc")
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, hint="winget install JohnMacFarlane.Pandoc", as_json=as_json)

    args: list[str] = [str(c) for c in chapters]
    if title:        args += ["--metadata", f"title={title}"]
    if author:       args += ["--metadata", f"author={author}"]
    for m in metadata: args += ["--metadata", m]
    if toc:          args.append("--toc")
    if toc_depth:    args.append(f"--toc-depth={toc_depth}")
    if bib:
        args += ["--citeproc", f"--bibliography={bib}"]
    if csl:          args.append(f"--csl={csl}")
    if css:          args.append(f"--css={css}")
    if engine:       args.append(f"--pdf-engine={engine}")
    if ref_doc:      args.append(f"--reference-doc={ref_doc}")
    if cover:        args += ["--epub-cover-image", str(cover)]

    if stream_progress:
        for c in chapters:
            sys.stderr.write(f'{{"chapter": "{c}"}}\n')
            sys.stderr.flush()

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
        emit_json({"chapters": [str(c) for c in chapters], "dst": str(dst)})
    elif not quiet:
        click.echo(f"wrote {dst} ({len(chapters)} chapters)")
