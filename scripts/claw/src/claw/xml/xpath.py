"""claw xml xpath — XPath 1.0 query with parameterized variables."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_USAGE, common_output_options, die, emit_json, read_text,
)


def _parse_kv(items: tuple[str, ...]) -> dict[str, str]:
    out: dict[str, str] = {}
    for it in items:
        if "=" not in it:
            raise click.BadParameter(f"expected K=V, got {it!r}")
        k, v = it.split("=", 1)
        out[k.strip()] = v
    return out


def _coerce(val: str) -> object:
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


@click.command(name="xpath")
@click.argument("src")
@click.argument("expression")
@click.option("--var", "variables", multiple=True, metavar="NAME=VALUE",
              help="Bind XPath variable (repeatable).")
@click.option("--ns", "namespaces", multiple=True, metavar="PREFIX=URI")
@click.option("--text", "as_text", is_flag=True)
@click.option("--html", "as_html_out", is_flag=True)
@click.option("--xml", "as_xml", is_flag=True, default=True)
@click.option("--attr", default=None)
@click.option("--count", is_flag=True)
@click.option("--allow-undeclared-vars", is_flag=True)
@click.option("--allow-entities", is_flag=True)
@click.option("--allow-network", is_flag=True)
@click.option("--huge-tree", is_flag=True)
@common_output_options
def xpath(src: str, expression: str, variables: tuple[str, ...],
          namespaces: tuple[str, ...], as_text: bool, as_html_out: bool, as_xml: bool,
          attr: str | None, count: bool, allow_undeclared_vars: bool,
          allow_entities: bool, allow_network: bool, huge_tree: bool,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Run an XPath 1.0 query against SRC."""
    try:
        from lxml import etree
    except ImportError:
        die("lxml not installed", code=EXIT_INPUT,
            hint="pip install 'claw[xml]'", as_json=as_json)

    try:
        vars_map = {k: _coerce(v) for k, v in _parse_kv(variables).items()}
        ns_map = _parse_kv(namespaces) or None
    except click.BadParameter as e:
        die(str(e), code=EXIT_USAGE, as_json=as_json)

    used_vars = set(re.findall(r"\$([A-Za-z_][A-Za-z0-9_]*)", expression))
    missing = used_vars - set(vars_map.keys())
    if missing and not allow_undeclared_vars:
        die(f"unbound XPath variables: {sorted(missing)}; use --var",
            code=EXIT_USAGE, as_json=as_json)

    parser = etree.XMLParser(
        resolve_entities=allow_entities,
        no_network=not allow_network,
        huge_tree=huge_tree,
    )
    xml_bytes = read_text(src).encode("utf-8")
    if dry_run:
        click.echo(f"would evaluate {expression!r} against {src}")
        return
    try:
        tree = etree.fromstring(xml_bytes, parser=parser)
    except etree.XMLSyntaxError as e:
        die(f"XML parse error: {e}", code=EXIT_INPUT, as_json=as_json)

    try:
        results = tree.xpath(expression, namespaces=ns_map, **vars_map)
    except etree.XPathEvalError as e:
        die(f"XPath error: {e}", code=EXIT_USAGE, as_json=as_json)

    if count:
        n = len(results) if isinstance(results, list) else 1
        if as_json:
            emit_json({"count": n})
        else:
            click.echo(n)
        return

    if not isinstance(results, list):
        results = [results]

    for r in results:
        if attr is not None and hasattr(r, "get"):
            v = r.get(attr)
            out = v or ""
        elif as_text:
            out = r.text_content() if hasattr(r, "text_content") else (
                r.text if hasattr(r, "text") and r.text else str(r))
        elif as_html_out:
            out = etree.tostring(r, encoding="unicode", method="html") if hasattr(r, "tag") else str(r)
        elif hasattr(r, "tag"):
            out = etree.tostring(r, encoding="unicode")
        else:
            out = str(r)
        if as_json:
            emit_json({"value": out})
        else:
            sys.stdout.write(out + "\n")
