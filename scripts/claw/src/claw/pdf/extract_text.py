"""claw pdf extract-text — text extraction via PyMuPDF."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from claw.common import PageSelector, die, emit_json, write_text


MODES = ("plain", "blocks", "dict", "html", "xhtml", "xml", "json")


@click.command(name="extract-text")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--pages", default="all", help="Page range (e.g. 1-5,7,odd,z-1,all).")
@click.option("--mode", type=click.Choice(MODES), default="plain")
@click.option("-o", "--out", default="-", type=click.Path(path_type=Path),
              help="Output file or `-` for stdout.")
@click.option("--dehyphenate", is_flag=True, help="Merge hyphenated line-break words.")
@click.option("--preserve-ligatures", is_flag=True, help="Keep ligature glyphs as-is.")
@click.option("--json", "as_json", is_flag=True, help="Emit JSON output.")
def extract_text(src: Path, pages: str, mode: str, out: Path, dehyphenate: bool,
                 preserve_ligatures: bool, as_json: bool) -> None:
    """Extract text from <SRC> in one of PyMuPDF's output modes."""
    try:
        import fitz
    except ImportError:
        die("PyMuPDF not installed; install: pip install 'claw[pdf]'")

    flags = 0
    if not preserve_ligatures:
        flags |= fitz.TEXT_PRESERVE_LIGATURES ^ fitz.TEXT_PRESERVE_LIGATURES
    if dehyphenate:
        flags |= fitz.TEXT_DEHYPHENATE

    doc = fitz.open(str(src))
    try:
        page_nums = PageSelector(pages).resolve(doc.page_count)
        chunks: list = []
        for n in page_nums:
            page = doc.load_page(n - 1)
            if mode == "plain":
                chunks.append(page.get_text("text", flags=flags) if flags
                              else page.get_text("text"))
            elif mode == "blocks":
                blocks = page.get_text("blocks", flags=flags) if flags \
                    else page.get_text("blocks")
                chunks.append({"page": n, "blocks": [list(b) for b in blocks]})
            elif mode == "dict":
                chunks.append({"page": n, **page.get_text("dict")})
            elif mode == "json":
                chunks.append({"page": n, **json.loads(page.get_text("json"))})
            else:
                chunks.append(page.get_text(mode))
    finally:
        doc.close()

    if as_json or mode in ("blocks", "dict", "json"):
        if str(out) in ("-", ""):
            emit_json(chunks)
        else:
            Path(out).write_text(json.dumps(chunks, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
        return

    text = "\n".join(chunks) if mode == "plain" else "\n\n".join(chunks)
    write_text(str(out), text)
