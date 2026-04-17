"""claw pdf split — split by ranges or per page."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import PageSelector, die, emit_json


@click.command(name="split")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--ranges", "ranges_spec", default=None,
              help='Comma-list of ranges, e.g. "1-5,6-end". One output per range.')
@click.option("--per-page", is_flag=True, help="Emit one output per page.")
@click.option("--out-dir", required=True, type=click.Path(path_type=Path))
@click.option("--name-template", default="{stem}_{n:04d}.pdf",
              help="Template: {stem} {n} {start} {end}.")
@click.option("--force", is_flag=True)
@click.option("--json", "as_json", is_flag=True)
@click.option("--dry-run", is_flag=True)
@click.option("--quiet", "-q", is_flag=True)
def split_(src: Path, ranges_spec: str | None, per_page: bool, out_dir: Path,
           name_template: str, force: bool, as_json: bool, dry_run: bool,
           quiet: bool) -> None:
    """Split <SRC> into multiple PDFs under --out-dir."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        die("pypdf not installed; install: pip install 'claw[pdf]'")

    if not (ranges_spec or per_page):
        die("pass --per-page or --ranges", code=2)
    if ranges_spec and per_page:
        die("--ranges and --per-page are mutually exclusive", code=2)

    reader = PdfReader(str(src))
    total = len(reader.pages)
    stem = src.stem

    jobs: list[tuple[str, list[int]]] = []
    if per_page:
        for n in range(1, total + 1):
            name = name_template.format(stem=stem, n=n, start=n, end=n)
            jobs.append((name, [n]))
    else:
        parts = [r.strip() for r in (ranges_spec or "").split(",") if r.strip()]
        for idx, part in enumerate(parts, start=1):
            pages = PageSelector(part).resolve(total)
            if not pages:
                continue
            name = name_template.format(stem=stem, n=idx,
                                        start=pages[0], end=pages[-1])
            jobs.append((name, pages))

    if dry_run:
        if as_json:
            emit_json([{"file": n, "pages": p} for n, p in jobs])
        else:
            for name, pages in jobs:
                click.echo(f"would write {out_dir / name} ({len(pages)} pages)")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, pages in jobs:
        dst = out_dir / name
        if dst.exists() and not force:
            die(f"{dst} exists (pass --force)")
        writer = PdfWriter()
        for p in pages:
            writer.add_page(reader.pages[p - 1])
        with open(dst, "wb") as f:
            writer.write(f)
        written.append(str(dst))

    if as_json:
        emit_json({"out_dir": str(out_dir), "files": written, "count": len(written)})
    elif not quiet:
        click.echo(f"wrote {len(written)} files to {out_dir}")
