"""claw xml canonicalize — emit C14N form for signing / diffing / hashing."""
from __future__ import annotations

import io
import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


@click.command(name="canonicalize")
@click.argument("src")
@click.option("--version", default="1.0",
              type=click.Choice(["1.0", "1.1", "2.0"]))
@click.option("--with-comments", is_flag=True)
@click.option("--exclusive", is_flag=True, help="Exclusive canonicalization (ExcC14N).")
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def canonicalize(src: str, version: str, with_comments: bool, exclusive: bool,
                 out: Path | None, force: bool, backup: bool, as_json: bool,
                 dry_run: bool, quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Emit canonical XML."""
    try:
        from lxml import etree
    except ImportError:
        die("lxml not installed", code=EXIT_INPUT,
            hint="pip install 'claw[xml]'", as_json=as_json)

    xml_bytes = read_text(src).encode("utf-8")
    if dry_run:
        click.echo(f"would canonicalize {src}")
        return

    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)
    try:
        tree = etree.fromstring(xml_bytes, parser=parser).getroottree()
    except etree.XMLSyntaxError as e:
        die(f"XML parse error: {e}", code=EXIT_INPUT, as_json=as_json)

    buf = io.BytesIO()
    if version == "2.0":
        etree.tostring(tree, method="c14n2", write=buf,
                       with_comments=with_comments)
    else:
        tree.write_c14n(buf, exclusive=exclusive, with_comments=with_comments)
    result = buf.getvalue()

    if out is None or str(out) == "-":
        sys.stdout.buffer.write(result)
    else:
        safe_write(out, lambda f: f.write(result),
                   force=force, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {out}", err=True)

    if as_json:
        emit_json({"bytes": len(result), "version": version})
