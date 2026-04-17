"""claw pptx add-image — insert a picture on a slide."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="add-image")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--slide", required=True, type=int)
@click.option("--image", "image_path", required=True,
              type=click.Path(exists=True, path_type=Path))
@click.option("--at", "at_pos", default="C", help="TL|TR|BL|BR|C or x,y")
@click.option("--size", default=None, help="w,h (e.g. 4in,3in)")
@click.option("--keep-aspect", "keep_aspect", is_flag=True)
@common_output_options
def add_image(src: Path, slide: int, image_path: Path,
              at_pos: str, size: str | None, keep_aspect: bool,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Insert a picture on a slide with optional sizing / anchor position."""
    try:
        from pptx import Presentation
        from pptx.util import Emu
    except ImportError:
        die("python-pptx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[pptx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would add {image_path} on slide {slide}")
        return

    prs = Presentation(str(src))
    target = prs.slides[slide - 1]

    w = h = None
    if size:
        ws, hs = size.split(",")
        w = _to_emu(ws)
        h = _to_emu(hs)

    slide_w, slide_h = prs.slide_width, prs.slide_height
    box_w = w or Emu(int(slide_w * 0.5))
    box_h = h or Emu(int(slide_h * 0.5))

    anchors = {
        "TL": (Emu(0), Emu(0)),
        "TR": (slide_w - box_w, Emu(0)),
        "BL": (Emu(0), slide_h - box_h),
        "BR": (slide_w - box_w, slide_h - box_h),
        "C":  ((slide_w - box_w) // 2, (slide_h - box_h) // 2),
    }
    if at_pos.upper() in anchors:
        x, y = anchors[at_pos.upper()]
    else:
        xs, ys = at_pos.split(",")
        x, y = _to_emu(xs), _to_emu(ys)

    kwargs = {}
    if w and not keep_aspect:
        kwargs["width"] = w
    if h and not keep_aspect:
        kwargs["height"] = h
    if keep_aspect and w:
        kwargs["width"] = w
    elif keep_aspect and h:
        kwargs["height"] = h

    target.shapes.add_picture(str(image_path), x, y, **kwargs)

    def _save(f):
        prs.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "slide": slide, "image": str(image_path)})
    elif not quiet:
        click.echo(f"added image to slide {slide}")


def _to_emu(spec: str):
    from pptx.util import Inches, Cm, Pt, Emu
    spec = spec.strip().lower()
    if spec.endswith("in"):
        return Inches(float(spec[:-2]))
    if spec.endswith("cm"):
        return Cm(float(spec[:-2]))
    if spec.endswith("pt"):
        return Pt(float(spec[:-2]))
    return Emu(int(spec))
