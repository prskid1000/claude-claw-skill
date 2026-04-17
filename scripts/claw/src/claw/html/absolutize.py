"""claw html absolutize — resolve relative URLs against a base."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


@click.command(name="absolutize")
@click.argument("src")
@click.option("--base", required=True, help="Base URL to resolve against.")
@click.option("--attrs", default="href,src,action,poster,srcset",
              help="Comma-separated link-bearing attributes.")
@click.option("--in-place", is_flag=True)
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def absolutize(src: str, base: str, attrs: str, in_place: bool, out: Path | None,
               force: bool, backup: bool, as_json: bool, dry_run: bool,
               quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Rewrite relative URLs to absolute form."""
    try:
        from lxml import html as lxml_html, etree
    except ImportError:
        die("lxml not installed", code=EXIT_INPUT,
            hint="pip install 'claw[html]'", as_json=as_json)

    html = read_text(src)
    if dry_run:
        click.echo(f"would absolutize {src} against {base}")
        return

    doc = lxml_html.fromstring(html)
    doc.make_links_absolute(base, resolve_base_href=True)
    result = etree.tostring(doc, encoding="unicode", method="html")

    dst = Path(src) if in_place and src != "-" else out
    if dst is None or str(dst) == "-":
        sys.stdout.write(result)
    else:
        safe_write(dst, lambda f: f.write(result.encode("utf-8")),
                   force=force or in_place, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {dst}", err=True)

    if as_json:
        emit_json({"output_bytes": len(result.encode("utf-8")), "base": base})
