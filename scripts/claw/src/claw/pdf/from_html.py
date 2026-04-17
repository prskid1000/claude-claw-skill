"""claw pdf from-html — HTML → PDF via PyMuPDF Story API."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import common_output_options, die, emit_json, safe_write


PAGE_SIZES = {
    "Letter": (612, 792),
    "Legal":  (612, 1008),
    "A4":     (595, 842),
    "A3":     (842, 1191),
}


@click.command(name="from-html")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("out", type=click.Path(path_type=Path))
@click.option("--page-size", default="Letter", type=click.Choice(list(PAGE_SIZES)))
@click.option("--rect", default=None, help='Content rect "x0,y0,x1,y1" in points.')
@click.option("--css", "css_file", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              default=None)
@common_output_options
def from_html(src: Path, out: Path, page_size: str, rect: str | None, css_file: Path | None,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Convert HTML <SRC> to PDF <OUT> via PyMuPDF Story."""
    try:
        import fitz
    except ImportError:
        die("PyMuPDF not installed; install: pip install 'claw[pdf]'")

    html = src.read_text(encoding="utf-8")
    css = css_file.read_text(encoding="utf-8") if css_file else None

    w, h = PAGE_SIZES[page_size]
    if rect:
        coords = [float(x) for x in rect.split(",")]
        if len(coords) != 4:
            die("--rect must be x0,y0,x1,y1", code=2)
        content_rect = fitz.Rect(*coords)
    else:
        content_rect = fitz.Rect(72, 72, w - 72, h - 72)

    if dry_run:
        click.echo(f"would render {src} → {out} ({page_size})")
        return

    story = fitz.Story(html=html, user_css=css) if css else fitz.Story(html=html)
    writer = fitz.DocumentWriter(str(out))
    more = True
    pages = 0
    while more:
        device = writer.begin_page(fitz.Rect(0, 0, w, h))
        more, _ = story.place(content_rect)
        story.draw(device)
        writer.end_page()
        pages += 1
        if pages > 10000:
            die("runaway page generation (>10000)")
    writer.close()

    if as_json:
        emit_json({"out": str(out), "pages": pages, "page_size": page_size})
    elif not quiet:
        click.echo(f"wrote {out} ({pages} pages)")
