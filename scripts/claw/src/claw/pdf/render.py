"""claw pdf render — rasterize a page to an image."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import common_output_options, die, safe_write


@click.command(name="render")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--page", "page_num", type=int, required=True, help="1-indexed page number.")
@click.option("-o", "--out", required=True, type=click.Path(path_type=Path))
@click.option("--dpi", type=int, default=150)
@click.option("--zoom", type=float, default=None, help="Alternative to --dpi (e.g. 2.0 = 144dpi).")
@click.option("--colorspace", type=click.Choice(["rgb", "gray", "cmyk"]), default="rgb")
@click.option("--clip", help="Clip rect x0,y0,x1,y1 in PDF points (top-left origin).")
@click.option("--no-annots", is_flag=True, help="Do not render annotations.")
@common_output_options
def render(src: Path, page_num: int, out: Path, dpi: int, zoom: float | None,
           colorspace: str, clip: str | None, no_annots: bool,
           force: bool, backup: bool, as_json: bool, dry_run: bool,
           quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Render <SRC> page N to --out FILE.png|.jpg."""
    try:
        import fitz
    except ImportError:
        die("PyMuPDF not installed; install: pip install 'claw[pdf]'")

    doc = fitz.open(str(src))
    try:
        if not 1 <= page_num <= doc.page_count:
            die(f"--page {page_num} out of range (1..{doc.page_count})")
        page = doc.load_page(page_num - 1)
        scale = zoom if zoom is not None else (dpi / 72.0)
        matrix = fitz.Matrix(scale, scale)
        cs_map = {"rgb": fitz.csRGB, "gray": fitz.csGRAY, "cmyk": fitz.csCMYK}
        kwargs: dict = {"matrix": matrix, "colorspace": cs_map[colorspace],
                        "annots": not no_annots}
        if clip:
            coords = [float(x) for x in clip.split(",")]
            if len(coords) != 4:
                die("--clip must be x0,y0,x1,y1")
            kwargs["clip"] = fitz.Rect(*coords)

        pix = page.get_pixmap(**kwargs)
        suffix = out.suffix.lower().lstrip(".") or "png"
        data = pix.tobytes(output=suffix)
    finally:
        doc.close()

    if dry_run:
        click.echo(f"would render page {page_num} → {out} ({len(data)} bytes)")
        return

    safe_write(out, lambda f: f.write(data), force=force, backup=backup, mkdir=mkdir)
    if as_json:
        from claw.common import emit_json
        emit_json({"out": str(out), "page": page_num, "bytes": len(data), "dpi": dpi})
    elif not quiet:
        click.echo(f"wrote {out} ({len(data)} bytes)")
