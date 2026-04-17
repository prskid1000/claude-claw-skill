"""claw pdf ocr — PyMuPDF + Tesseract text layer over scanned pages."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import PageSelector, common_output_options, die, emit_json, safe_write


@click.command(name="ocr")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--lang", default="eng", help="Tesseract language codes, e.g. eng+fra.")
@click.option("--dpi", type=int, default=300)
@click.option("--sidecar", is_flag=True, help="Also write <out>.txt.")
@click.option("--pages", default="all")
@click.option("-o", "--out", type=click.Path(path_type=Path), default=None)
@click.option("--in-place", is_flag=True)
@common_output_options
def ocr(src: Path, lang: str, dpi: int, sidecar: bool, pages: str,
        out: Path | None, in_place: bool,
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Add an OCR text layer over <SRC> pages (requires tesseract on PATH)."""
    try:
        import fitz
    except ImportError:
        die("PyMuPDF not installed; install: pip install 'claw[pdf]'")

    if not (out or in_place):
        die("pass --out FILE or --in-place", code=2)
    target = src if in_place else out
    assert target is not None

    doc = fitz.open(str(src))
    try:
        page_nums = PageSelector(pages).resolve(doc.page_count)
        ocr_text_parts: list[str] = []
        for n in page_nums:
            page = doc.load_page(n - 1)
            try:
                tp = page.get_textpage_ocr(language=lang, dpi=dpi, full=True)
            except RuntimeError as e:
                die(f"OCR failed on page {n}: {e}",
                    hint="ensure tesseract is on PATH; check `claw doctor`", code=5)
            if sidecar:
                ocr_text_parts.append(page.get_text(textpage=tp))
            page.apply_redactions = getattr(page, "apply_redactions", lambda: None)

        if dry_run:
            click.echo(f"would OCR {len(page_nums)} pages (lang={lang}) → {target}")
            return

        data = doc.tobytes(deflate=True)
    finally:
        doc.close()

    safe_write(target, lambda f: f.write(data),
               force=force or in_place, backup=backup, mkdir=mkdir)

    if sidecar:
        sidecar_path = Path(str(target) + ".txt")
        sidecar_path.write_text("\n\n".join(ocr_text_parts), encoding="utf-8")

    if as_json:
        emit_json({"out": str(target), "pages": len(page_nums), "lang": lang,
                   "sidecar": str(target) + ".txt" if sidecar else None})
    elif not quiet:
        click.echo(f"OCR'd {len(page_nums)} pages → {target}")
