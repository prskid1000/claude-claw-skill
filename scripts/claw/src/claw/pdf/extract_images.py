"""claw pdf extract-images — dump embedded images to a directory."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import PageSelector, die, emit_json


@click.command(name="extract-images")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--out", "out_dir", required=True, type=click.Path(path_type=Path),
              help="Output directory.")
@click.option("--pages", default="all", help="Page range.")
@click.option("--format", "fmt", type=click.Choice(["png", "jpeg", "original"]),
              default="original")
@click.option("--min-width", type=int, default=0)
@click.option("--min-height", type=int, default=0)
@click.option("--json", "as_json", is_flag=True)
@click.option("--quiet", "-q", is_flag=True)
def extract_images(src: Path, out_dir: Path, pages: str, fmt: str,
                   min_width: int, min_height: int, as_json: bool, quiet: bool) -> None:
    """Extract embedded images from <SRC> into --out DIR."""
    try:
        import fitz
    except ImportError:
        die("PyMuPDF not installed; install: pip install 'claw[pdf]'")

    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(src))
    records: list[dict] = []
    try:
        page_nums = PageSelector(pages).resolve(doc.page_count)
        for n in page_nums:
            page = doc.load_page(n - 1)
            for img_idx, info in enumerate(page.get_images(full=True)):
                xref = info[0]
                data = doc.extract_image(xref)
                w, h = data.get("width", 0), data.get("height", 0)
                if w < min_width or h < min_height:
                    continue
                ext = data["ext"]
                img_bytes = data["image"]
                if fmt != "original" and ext != fmt:
                    pix = fitz.Pixmap(data["image"])
                    if pix.colorspace and pix.colorspace.n > 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    img_bytes = pix.tobytes(fmt)
                    ext = fmt
                    pix = None
                name = f"page{n:04d}_img{img_idx:03d}.{ext}"
                (out_dir / name).write_bytes(img_bytes)
                records.append({"page": n, "index": img_idx, "file": name,
                                "width": w, "height": h, "xref": xref})
    finally:
        doc.close()

    if as_json:
        emit_json({"count": len(records), "out_dir": str(out_dir), "images": records})
    elif not quiet:
        click.echo(f"wrote {len(records)} images to {out_dir}")
