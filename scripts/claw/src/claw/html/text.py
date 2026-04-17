"""claw html text — flatten HTML to text."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


@click.command(name="text")
@click.argument("src")
@click.option("--css", default=None, help="Restrict to matched subtree.")
@click.option("--xpath", default=None)
@click.option("--sep", default="\n", help="Separator between navigable strings.")
@click.option("--strip", is_flag=True, help="Collapse whitespace / trim strings.")
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def text(src: str, css: str | None, xpath: str | None, sep: str, strip: bool,
         out: Path | None, force: bool, backup: bool, as_json: bool, dry_run: bool,
         quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Extract flattened text from HTML."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        die("beautifulsoup4 not installed", code=EXIT_INPUT,
            hint="pip install 'claw[html]'", as_json=as_json)

    html = read_text(src)
    if dry_run:
        click.echo(f"would extract text from {src}")
        return

    soup = BeautifulSoup(html, "lxml")
    if xpath:
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html)
        nodes = tree.xpath(xpath)
        chunks = []
        for n in nodes:
            chunks.append(n.text_content() if hasattr(n, "text_content") else str(n))
        result = sep.join(chunks)
    elif css:
        nodes = soup.select(css)
        result = sep.join(n.get_text(separator=sep, strip=strip) for n in nodes)
    else:
        result = soup.get_text(separator=sep, strip=strip)

    if strip and (xpath or not css):
        result = sep.join(line.strip() for line in result.split(sep) if line.strip())

    if as_json:
        emit_json({"text": result, "bytes": len(result.encode("utf-8"))})
        return

    if out is None or str(out) == "-":
        sys.stdout.write(result)
        if not result.endswith("\n"):
            sys.stdout.write("\n")
    else:
        safe_write(out, lambda f: f.write(result.encode("utf-8")),
                   force=force, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {out}", err=True)
