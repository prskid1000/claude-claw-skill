"""claw pdf redact — remove text + pixels via PyMuPDF apply_redactions."""
from __future__ import annotations

import json
import re
from pathlib import Path

import click

from claw.common import PageSelector, common_output_options, die, emit_json, safe_write


def _hex_to_rgb(h: str) -> tuple[float, float, float]:
    s = h.lstrip("#")
    r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    return (r / 255, g / 255, b / 255)


@click.command(name="redact")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--regex", "regex_pat", default=None, help="Regex matched on page text.")
@click.option("--terms", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              default=None, help="Newline-separated literal terms.")
@click.option("--boxes", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              default=None, help="JSON list of {page,x0,y0,x1,y1}.")
@click.option("--preview", type=click.Path(path_type=Path), default=None,
              help="Render preview PNG without applying.")
@click.option("--fill", default="#000000")
@click.option("--dehyphenate", is_flag=True)
@click.option("--pages", default="all")
@click.option("-o", "--out", type=click.Path(path_type=Path), default=None)
@click.option("--in-place", is_flag=True)
@common_output_options
def redact(src: Path, regex_pat: str | None, terms: Path | None, boxes: Path | None,
           preview: Path | None, fill: str, dehyphenate: bool, pages: str,
           out: Path | None, in_place: bool,
           force: bool, backup: bool, as_json: bool, dry_run: bool,
           quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Redact matches from <SRC> — text + pixels."""
    try:
        import fitz
    except ImportError:
        die("PyMuPDF not installed; install: pip install 'claw[pdf]'")

    if not any([regex_pat, terms, boxes]):
        die("pass --regex, --terms, or --boxes", code=2)
    if not (out or in_place or preview):
        die("pass --out, --in-place, or --preview", code=2)

    term_list: list[str] = []
    if terms:
        term_list = [line.strip() for line in terms.read_text(encoding="utf-8").splitlines()
                     if line.strip()]

    box_list: list[dict] = []
    if boxes:
        box_list = json.loads(boxes.read_text(encoding="utf-8"))

    rgb = _hex_to_rgb(fill)
    doc = fitz.open(str(src))
    target_pages = set(PageSelector(pages).resolve(doc.page_count))
    match_count = 0

    try:
        for i in range(doc.page_count):
            page_no = i + 1
            if page_no not in target_pages:
                continue
            page = doc.load_page(i)

            rects: list = []
            if regex_pat:
                flags = fitz.TEXT_DEHYPHENATE if dehyphenate else 0
                text = page.get_text("text", flags=flags)
                for m in re.finditer(regex_pat, text):
                    for rect in page.search_for(m.group(0)):
                        rects.append(rect)
            for term in term_list:
                for rect in page.search_for(term):
                    rects.append(rect)
            for b in box_list:
                if b.get("page") == page_no:
                    rects.append(fitz.Rect(b["x0"], b["y0"], b["x1"], b["y1"]))

            match_count += len(rects)
            for rect in rects:
                page.add_redact_annot(rect, fill=rgb)

            if preview is None and not dry_run:
                page.apply_redactions()

        if preview:
            if not target_pages:
                die("no pages to preview")
            first = sorted(target_pages)[0]
            pix = doc.load_page(first - 1).get_pixmap(dpi=150)
            data = pix.tobytes("png")
            safe_write(preview, lambda f: f.write(data),
                       force=force, backup=backup, mkdir=mkdir)
            if not quiet:
                click.echo(f"preview → {preview} ({match_count} marks)")
            return

        if dry_run:
            click.echo(f"would redact {match_count} matches across {len(target_pages)} pages")
            return

        target = src if in_place else out
        assert target is not None
        data = doc.tobytes()
    finally:
        doc.close()

    safe_write(target, lambda f: f.write(data),
               force=force or in_place, backup=backup, mkdir=mkdir)
    if as_json:
        emit_json({"out": str(target), "matches": match_count,
                   "pages": sorted(target_pages)})
    elif not quiet:
        click.echo(f"redacted {match_count} matches → {target}")
