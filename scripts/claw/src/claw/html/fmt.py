"""claw html fmt — prettify HTML."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


@click.command(name="fmt")
@click.argument("src")
@click.option("--formatter", default="minimal",
              type=click.Choice(["minimal", "html", "html5", "none"]))
@click.option("--indent", default=2, type=int)
@click.option("--in-place", is_flag=True)
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def fmt(src: str, formatter: str, indent: int, in_place: bool, out: Path | None,
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Pretty-print HTML."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        die("beautifulsoup4 not installed", code=EXIT_INPUT,
            hint="pip install 'claw[html]'", as_json=as_json)

    html = read_text(src)
    if dry_run:
        click.echo(f"would format {src}")
        return

    soup = BeautifulSoup(html, "lxml")
    fmt_arg = None if formatter == "none" else formatter
    result = soup.prettify(formatter=fmt_arg)

    if indent != 1 and formatter != "none":
        pad = " " * indent
        out_lines = []
        for line in result.split("\n"):
            stripped = line.lstrip(" ")
            depth = len(line) - len(stripped)
            out_lines.append(pad * depth + stripped)
        result = "\n".join(out_lines)

    dst = Path(src) if in_place and src != "-" else out
    if dst is None or str(dst) == "-":
        sys.stdout.write(result)
    else:
        safe_write(dst, lambda f: f.write(result.encode("utf-8")),
                   force=force or in_place, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {dst}", err=True)

    if as_json:
        emit_json({"output_bytes": len(result.encode("utf-8")), "formatter": formatter})
