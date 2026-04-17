"""claw pdf search — find a term and return page + bounding boxes."""
from __future__ import annotations

import re
from pathlib import Path

import click

from claw.common import PageSelector, die, emit_json


@click.command(name="search")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--term", required=True)
@click.option("--regex", "is_regex", is_flag=True)
@click.option("--case-sensitive", is_flag=True)
@click.option("--pages", default="all")
@click.option("--context", "context_chars", type=int, default=40)
@click.option("--json", "as_json", is_flag=True)
def search(src: Path, term: str, is_regex: bool, case_sensitive: bool,
           pages: str, context_chars: int, as_json: bool) -> None:
    """Search <SRC> for --term, return page + bbox + context."""
    try:
        import fitz
    except ImportError:
        die("PyMuPDF not installed; install: pip install 'claw[pdf]'")

    doc = fitz.open(str(src))
    hits: list[dict] = []
    try:
        page_nums = PageSelector(pages).resolve(doc.page_count)
        if is_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            pat = re.compile(term, flags)
        for n in page_nums:
            page = doc.load_page(n - 1)
            if is_regex:
                text = page.get_text("text")
                for m in pat.finditer(text):
                    matched = m.group(0)
                    rects = page.search_for(matched, quads=False)
                    start = max(0, m.start() - context_chars)
                    end = min(len(text), m.end() + context_chars)
                    ctx = text[start:end].replace("\n", " ")
                    for r in rects:
                        hits.append({"page": n, "match": matched, "context": ctx,
                                     "bbox": [r.x0, r.y0, r.x1, r.y1]})
                    if not rects:
                        hits.append({"page": n, "match": matched, "context": ctx,
                                     "bbox": None})
            else:
                rect_flags = 0 if case_sensitive else fitz.TEXT_DEHYPHENATE
                rects = page.search_for(term, quads=False)
                for r in rects:
                    hits.append({"page": n, "match": term,
                                 "bbox": [r.x0, r.y0, r.x1, r.y1]})
    finally:
        doc.close()

    if as_json:
        emit_json({"term": term, "count": len(hits), "hits": hits})
        return

    if not hits:
        click.echo("no matches")
        return
    for h in hits:
        bbox = h.get("bbox")
        bbox_str = f" [{bbox[0]:.1f},{bbox[1]:.1f},{bbox[2]:.1f},{bbox[3]:.1f}]" \
            if bbox else ""
        ctx = h.get("context")
        ctx_str = f"  {ctx}" if ctx else ""
        click.echo(f"p{h['page']}{bbox_str}{ctx_str}")
    click.echo(f"── {len(hits)} match(es)")
