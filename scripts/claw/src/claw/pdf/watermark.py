"""claw pdf watermark — diagonal text watermark across pages."""
from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import PageSelector, common_output_options, die, emit_json, safe_write


def _hex_to_rgb(h: str) -> tuple[float, float, float]:
    s = h.lstrip("#")
    if len(s) not in (6, 8):
        raise ValueError(f"bad color: {h}")
    r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    return (r / 255, g / 255, b / 255)


@click.command(name="watermark")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--text", required=True, help="Watermark text.")
@click.option("--opacity", type=float, default=0.2)
@click.option("--rotate", "rotate_deg", type=float, default=45)
@click.option("--color", default="#888888")
@click.option("--font", default="Helvetica")
@click.option("--size", "font_size", type=int, default=64)
@click.option("--pages", default="all")
@click.option("--layer", type=click.Choice(["behind", "above"]), default="above")
@click.option("-o", "--out", type=click.Path(path_type=Path), default=None)
@click.option("--in-place", is_flag=True)
@common_output_options
def watermark(src: Path, text: str, opacity: float, rotate_deg: float, color: str,
              font: str, font_size: int, pages: str, layer: str,
              out: Path | None, in_place: bool,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Stamp --text across pages of <SRC>."""
    try:
        from pypdf import PdfReader, PdfWriter, Transformation
        from pypdf.generic import RectangleObject
    except ImportError:
        die("pypdf not installed; install: pip install 'claw[pdf]'")
    try:
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.lib.pagesizes import letter
    except ImportError:
        die("reportlab not installed; install: pip install 'claw[pdf]'")

    if not (out or in_place):
        die("pass --out FILE or --in-place", code=2)
    target = src if in_place else out

    reader = PdfReader(str(src))
    total = len(reader.pages)
    target_pages = set(PageSelector(pages).resolve(total))
    r, g, b = _hex_to_rgb(color)

    def build_overlay(w: float, h: float) -> bytes:
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=(w, h))
        c.setFillColorRGB(r, g, b, alpha=opacity)
        c.setFont(font, font_size)
        c.saveState()
        c.translate(w / 2, h / 2)
        c.rotate(rotate_deg)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        c.showPage()
        c.save()
        return buf.getvalue()

    writer = PdfWriter()
    for i, page in enumerate(reader.pages, start=1):
        if i in target_pages:
            box = page.mediabox
            w = float(box.width)
            h = float(box.height)
            overlay_reader = PdfReader(io.BytesIO(build_overlay(w, h)))
            stamp = overlay_reader.pages[0]
            if layer == "behind":
                base = writer.add_blank_page(w, h)
                base.merge_page(stamp)
                base.merge_page(page)
            else:
                page.merge_page(stamp)
                writer.add_page(page)
        else:
            writer.add_page(page)

    if dry_run:
        click.echo(f"would stamp {len(target_pages)} pages with {text!r} → {target}")
        return

    safe_write(target, lambda f: writer.write(f),
               force=force or in_place, backup=backup, mkdir=mkdir)
    if as_json:
        emit_json({"out": str(target), "pages_stamped": len(target_pages), "text": text})
    elif not quiet:
        click.echo(f"stamped {len(target_pages)} pages → {target}")
