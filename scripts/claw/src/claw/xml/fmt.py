"""claw xml fmt — pretty-print XML."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


def _sort_attrs(elem) -> None:
    for e in elem.iter():
        if len(e.attrib) > 1:
            items = sorted(e.attrib.items())
            e.attrib.clear()
            for k, v in items:
                e.set(k, v)


@click.command(name="fmt")
@click.argument("src")
@click.option("--indent", default=2, type=int)
@click.option("--sort-attrs", is_flag=True, help="Deterministic attribute order.")
@click.option("--declaration", is_flag=True, help="Emit <?xml...?> declaration.")
@click.option("--encoding", default="utf-8")
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def fmt(src: str, indent: int, sort_attrs: bool, declaration: bool, encoding: str,
        out: Path | None, force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Pretty-print XML with configurable indent."""
    try:
        from lxml import etree
    except ImportError:
        die("lxml not installed", code=EXIT_INPUT,
            hint="pip install 'claw[xml]'", as_json=as_json)

    xml_bytes = read_text(src).encode("utf-8")
    if dry_run:
        click.echo(f"would format {src}")
        return

    parser = etree.XMLParser(resolve_entities=False, no_network=True,
                             huge_tree=False, remove_blank_text=True)
    try:
        tree = etree.fromstring(xml_bytes, parser=parser)
    except etree.XMLSyntaxError as e:
        die(f"XML parse error: {e}", code=EXIT_INPUT, as_json=as_json)

    if sort_attrs:
        _sort_attrs(tree)

    etree.indent(tree, space=" " * indent)
    result = etree.tostring(
        tree, pretty_print=True, xml_declaration=declaration,
        encoding=encoding,
    )

    if out is None or str(out) == "-":
        sys.stdout.buffer.write(result)
    else:
        safe_write(out, lambda f: f.write(result),
                   force=force, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {out}", err=True)

    if as_json:
        emit_json({"bytes": len(result)})
