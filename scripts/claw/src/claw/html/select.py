"""claw html select — CSS/XPath query, htmlq-style."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_USAGE, NodeSelector, common_output_options, die, emit_json,
    read_text, safe_write,
)


@click.command(name="select")
@click.argument("src")
@click.option("--css", default=None, help="CSS selector.")
@click.option("--xpath", default=None, help="XPath expression.")
@click.option("--all", "all_matches", is_flag=True, default=True)
@click.option("--index", default=None, type=int, help="1-based index of a single match.")
@click.option("--attr", default=None, help="Emit this attribute's value.")
@click.option("--text", "as_text", is_flag=True, help="Emit text content.")
@click.option("--html", "as_html", is_flag=True, help="Emit outer HTML (default).")
@click.option("--sep", default="\n", help="Join separator.")
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def select(src: str, css: str | None, xpath: str | None, all_matches: bool,
           index: int | None, attr: str | None, as_text: bool, as_html: bool,
           sep: str, out: Path | None, force: bool, backup: bool, as_json: bool,
           dry_run: bool, quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Query HTML with CSS or XPath."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        die("beautifulsoup4 not installed", code=EXIT_INPUT,
            hint="pip install 'claw[html]'", as_json=as_json)

    if not css and not xpath:
        die("provide --css or --xpath", code=EXIT_USAGE, as_json=as_json)

    html = read_text(src)
    if dry_run:
        click.echo(f"would select from {src}")
        return

    matches: list = []
    if xpath or (css and NodeSelector(css).kind == "xpath"):
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(html)
        matches = tree.xpath(xpath or css)
    else:
        soup = BeautifulSoup(html, "lxml")
        matches = soup.select(css)

    if index is not None:
        if index < 1 or index > len(matches):
            die(f"--index {index} out of range (1..{len(matches)})",
                code=EXIT_USAGE, as_json=as_json)
        matches = [matches[index - 1]]

    out_lines: list[str] = []
    json_records: list = []
    for m in matches:
        if attr:
            v = m.get(attr) if hasattr(m, "get") else (m if isinstance(m, str) else "")
            out_lines.append(v or "")
            json_records.append({"attr": attr, "value": v})
        elif as_text:
            t = m.get_text() if hasattr(m, "get_text") else (
                m.text_content() if hasattr(m, "text_content") else str(m))
            out_lines.append(t)
            json_records.append({"text": t})
        else:
            if hasattr(m, "decode"):
                s = m.decode()
            elif hasattr(m, "getroottree"):
                from lxml import etree
                s = etree.tostring(m, encoding="unicode", method="html")
            else:
                s = str(m)
            out_lines.append(s)
            json_records.append({"html": s})

    if as_json:
        for r in json_records:
            emit_json(r)
        return

    content = sep.join(out_lines) + ("\n" if out_lines else "")
    if out is None or str(out) == "-":
        sys.stdout.write(content)
    else:
        safe_write(out, lambda f: f.write(content.encode("utf-8")),
                   force=force, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {out} ({len(matches)} match(es))", err=True)
