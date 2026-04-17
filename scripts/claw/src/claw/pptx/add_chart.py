"""claw pptx add-chart — insert a native PPT chart from CSV."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_rows, safe_write,
)


CHART_TYPE_MAP = {
    "bar":     "BAR_CLUSTERED",
    "col":     "COLUMN_CLUSTERED",
    "line":    "LINE",
    "pie":     "PIE",
    "scatter": "XY_SCATTER",
    "area":    "AREA",
}


@click.command(name="add-chart")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--slide", required=True, type=int, help="1-based slide index.")
@click.option("--type", "chart_type", required=True,
              type=click.Choice(list(CHART_TYPE_MAP.keys())))
@click.option("--data", "data_src", required=True)
@click.option("--at", "at_pos", default="1in,2in")
@click.option("--size", default="8in,4in")
@click.option("--title", default=None)
@click.option("--style", "style_n", default=None, type=int)
@common_output_options
def add_chart(src: Path, slide: int, chart_type: str, data_src: str,
              at_pos: str, size: str, title: str | None, style_n: int | None,
              force: bool, backup: bool, as_json: bool, dry_run: bool,
              quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Insert a bar/col/line/pie/scatter/area chart from a CSV."""
    try:
        from pptx import Presentation
        from pptx.chart.data import CategoryChartData, XyChartData
        from pptx.enum.chart import XL_CHART_TYPE
        from pptx.util import Emu
    except ImportError:
        die("python-pptx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[pptx]'", as_json=as_json)

    rows = read_rows(data_src, header=True)
    if not rows:
        die("no data rows", code=EXIT_INPUT, as_json=as_json)

    if dry_run:
        click.echo(f"would add {chart_type} chart on slide {slide}")
        return

    x, y = [_to_emu(v) for v in at_pos.split(",")]
    w, h = [_to_emu(v) for v in size.split(",")]

    prs = Presentation(str(src))
    target = prs.slides[slide - 1]
    xl_type = getattr(XL_CHART_TYPE, CHART_TYPE_MAP[chart_type])

    if chart_type == "scatter":
        data = XyChartData()
        headers = list(rows[0].keys()) if isinstance(rows[0], dict) else []
        for col in headers[1:]:
            series = data.add_series(col)
            for r in rows:
                series.add_data_point(float(r[headers[0]]), float(r[col]))
    else:
        data = CategoryChartData()
        if isinstance(rows[0], dict):
            headers = list(rows[0].keys())
            cat_key = headers[0]
            data.categories = [r[cat_key] for r in rows]
            for col in headers[1:]:
                data.add_series(col, [_num(r[col]) for r in rows])
        else:
            data.categories = [r[0] for r in rows[1:]]
            for ci, col in enumerate(rows[0][1:], start=1):
                data.add_series(col, [_num(r[ci]) for r in rows[1:]])

    chart_shape = target.shapes.add_chart(xl_type, x, y, w, h, data)
    chart = chart_shape.chart
    if title:
        chart.has_title = True
        chart.chart_title.text_frame.text = title
    if style_n is not None:
        chart.chart_style = style_n

    def _save(f):
        prs.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "slide": slide, "type": chart_type})
    elif not quiet:
        click.echo(f"added {chart_type} chart to slide {slide}")


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


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0
