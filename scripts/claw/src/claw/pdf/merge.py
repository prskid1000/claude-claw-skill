"""claw pdf merge — pdftk-style range-aware concatenation."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import PageSelector, common_output_options, die, emit_json, safe_write


@click.command(name="merge")
@click.argument("inputs", nargs=-1, required=True)
@click.option("-o", "--out", required=True, type=click.Path(path_type=Path))
@click.option("--toc-from", type=click.Choice(["filenames", "none"]), default="none",
              help="Build a top-level TOC entry per input file.")
@common_output_options
def merge(inputs: tuple[str, ...], out: Path, toc_from: str,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Merge INPUTS (each optionally `file.pdf:RANGE`) into --out."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        die("pypdf not installed; install: pip install 'claw[pdf]'")

    writer = PdfWriter()
    plan: list[dict] = []
    running = 0
    for spec in inputs:
        if ":" in spec and not Path(spec).exists():
            path_str, range_spec = spec.rsplit(":", 1)
        else:
            path_str, range_spec = spec, "all"
        if not Path(path_str).exists():
            die(f"input not found: {path_str}")
        reader = PdfReader(path_str)
        resolved = PageSelector(range_spec).resolve(len(reader.pages))
        plan.append({"file": path_str, "pages": len(resolved), "range": range_spec})
        start_page = running
        for p in resolved:
            writer.add_page(reader.pages[p - 1])
        running += len(resolved)
        if toc_from == "filenames":
            writer.add_outline_item(title=Path(path_str).stem, page_number=start_page)

    total = running
    if dry_run:
        if as_json:
            emit_json({"would_write": str(out), "total_pages": total, "inputs": plan})
        else:
            click.echo(f"would merge {total} pages from {len(inputs)} inputs → {out}")
            for p in plan:
                click.echo(f"  {p['file']}:{p['range']} ({p['pages']} pages)")
        return

    safe_write(out, lambda f: writer.write(f), force=force, backup=backup, mkdir=mkdir)
    if as_json:
        emit_json({"out": str(out), "total_pages": total, "inputs": plan})
    elif not quiet:
        click.echo(f"wrote {out} ({total} pages from {len(inputs)} inputs)")
