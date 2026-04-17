"""claw xml xslt — XSLT 1.0 transform."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_USAGE, common_output_options, die, emit_json, safe_write,
)


def _parse_kv(items: tuple[str, ...]) -> dict[str, str]:
    out: dict[str, str] = {}
    for it in items:
        if "=" not in it:
            raise click.BadParameter(f"expected K=V, got {it!r}")
        k, v = it.split("=", 1)
        out[k.strip()] = v
    return out


@click.command(name="xslt")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.argument("stylesheet", type=click.Path(exists=True, path_type=Path))
@click.option("--param", "params", multiple=True, metavar="KEY=VALUE",
              help="XSLT string param (quoted literal).")
@click.option("--param-xpath", "xpath_params", multiple=True, metavar="KEY=EXPR",
              help="XSLT param using raw XPath expression.")
@click.option("--out", default=None, type=click.Path(path_type=Path))
@click.option("--profile", default=None, type=click.Path(path_type=Path))
@common_output_options
def xslt(src: Path, stylesheet: Path, params: tuple[str, ...],
         xpath_params: tuple[str, ...], out: Path | None, profile: Path | None,
         force: bool, backup: bool, as_json: bool, dry_run: bool,
         quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Apply STYLESHEET to SRC (XSLT 1.0)."""
    try:
        from lxml import etree
    except ImportError:
        die("lxml not installed", code=EXIT_INPUT,
            hint="pip install 'claw[xml]'", as_json=as_json)

    try:
        str_params = _parse_kv(params)
        expr_params = _parse_kv(xpath_params)
    except click.BadParameter as e:
        die(str(e), code=EXIT_USAGE, as_json=as_json)

    if dry_run:
        click.echo(f"would transform {src} via {stylesheet}")
        return

    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)
    try:
        doc = etree.parse(str(src), parser=parser)
        xsl = etree.parse(str(stylesheet), parser=parser)
    except etree.XMLSyntaxError as e:
        die(f"parse error: {e}", code=EXIT_INPUT, as_json=as_json)

    transform = etree.XSLT(xsl)
    kwargs = {}
    for k, v in str_params.items():
        kwargs[k] = etree.XSLT.strparam(v)
    for k, v in expr_params.items():
        kwargs[k] = v

    try:
        result = transform(doc, **{k: v for k, v in kwargs.items()
                                   if k.isidentifier()},
                           profile_run=profile is not None)
    except etree.XSLTApplyError as e:
        die(f"XSLT error: {e}", code=EXIT_INPUT, as_json=as_json)

    if profile is not None and hasattr(result, "xslt_profile") and result.xslt_profile is not None:
        prof_bytes = etree.tostring(result.xslt_profile, pretty_print=True)
        profile.write_bytes(prof_bytes)

    out_bytes = bytes(result)
    if out is None or str(out) == "-":
        sys.stdout.buffer.write(out_bytes)
    else:
        safe_write(out, lambda f: f.write(out_bytes),
                   force=force, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {out}", err=True)

    if as_json:
        emit_json({"out": str(out) if out else None, "bytes": len(out_bytes)})
