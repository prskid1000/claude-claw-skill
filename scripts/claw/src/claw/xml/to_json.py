"""claw xml to-json — convert XML to JSON (literal or objectify style)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


def _coerce_scalar(s: str):
    s = s.strip()
    if s == "":
        return s
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _literal(elem) -> dict:
    d: dict = {"tag": elem.tag, "attrib": dict(elem.attrib)}
    if elem.text and elem.text.strip():
        d["text"] = elem.text
    children = [_literal(c) for c in elem]
    if children:
        d["children"] = children
    return d


def _objectify(elem):
    children = list(elem)
    if not children and not elem.attrib:
        return _coerce_scalar(elem.text or "")
    result: dict = {}
    if elem.attrib:
        for k, v in elem.attrib.items():
            result[f"@{k}"] = v
    if elem.text and elem.text.strip():
        result["#text"] = _coerce_scalar(elem.text)
    for child in children:
        tag = child.tag
        val = _objectify(child)
        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(val)
        else:
            result[tag] = val
    return result


@click.command(name="to-json")
@click.argument("src")
@click.option("--objectify", is_flag=True, help="Lossy ergonomic style.")
@click.option("--literal", is_flag=True, default=True, help="Structural style (default).")
@click.option("--out", default=None, type=click.Path(path_type=Path))
@click.option("--indent", default=2, type=int)
@common_output_options
def to_json(src: str, objectify: bool, literal: bool, out: Path | None, indent: int,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Convert XML to JSON."""
    try:
        from lxml import etree
    except ImportError:
        die("lxml not installed", code=EXIT_INPUT,
            hint="pip install 'claw[xml]'", as_json=as_json)

    xml_bytes = read_text(src).encode("utf-8")
    if dry_run:
        click.echo(f"would convert {src} to JSON")
        return

    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)
    try:
        root = etree.fromstring(xml_bytes, parser=parser)
    except etree.XMLSyntaxError as e:
        die(f"XML parse error: {e}", code=EXIT_INPUT, as_json=as_json)

    if objectify:
        data = {root.tag: _objectify(root)}
    else:
        data = _literal(root)

    text = json.dumps(data, indent=indent, ensure_ascii=False)

    if out is None or str(out) == "-":
        sys.stdout.write(text + "\n")
    else:
        safe_write(out, lambda f: f.write(text.encode("utf-8")),
                   force=force, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {out}", err=True)
