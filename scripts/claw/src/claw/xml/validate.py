"""claw xml validate — validate against XSD / RelaxNG / DTD."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_USAGE, common_output_options, die, emit_json,
)


@click.command(name="validate")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--xsd", default=None, type=click.Path(exists=True, path_type=Path))
@click.option("--rng", default=None, type=click.Path(exists=True, path_type=Path))
@click.option("--rnc", default=None, type=click.Path(exists=True, path_type=Path))
@click.option("--dtd", default=None, type=click.Path(exists=True, path_type=Path))
@click.option("--all-errors", is_flag=True, help="Report every error (not first-fail).")
@common_output_options
def validate(src: Path, xsd: Path | None, rng: Path | None, rnc: Path | None,
             dtd: Path | None, all_errors: bool,
             force: bool, backup: bool, as_json: bool, dry_run: bool,
             quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Validate SRC against a schema. Exit 6 on validation failure."""
    try:
        from lxml import etree
    except ImportError:
        die("lxml not installed", code=EXIT_INPUT,
            hint="pip install 'claw[xml]'", as_json=as_json)

    schemas = [x for x in ((xsd, "xsd"), (rng, "rng"), (rnc, "rnc"), (dtd, "dtd")) if x[0]]
    if len(schemas) != 1:
        die("exactly one of --xsd / --rng / --rnc / --dtd is required",
            code=EXIT_USAGE, as_json=as_json)
    schema_path, kind = schemas[0]

    if dry_run:
        click.echo(f"would validate {src} against {kind} {schema_path}")
        return

    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)
    try:
        doc = etree.parse(str(src), parser=parser)
    except etree.XMLSyntaxError as e:
        die(f"XML parse error: {e}", code=EXIT_INPUT, as_json=as_json)

    try:
        if kind == "xsd":
            schema = etree.XMLSchema(etree.parse(str(schema_path), parser=parser))
        elif kind == "rng":
            schema = etree.RelaxNG(etree.parse(str(schema_path), parser=parser))
        elif kind == "rnc":
            die("RelaxNG Compact (.rnc) not supported directly; convert to .rng first",
                code=EXIT_USAGE, as_json=as_json)
            return
        else:
            schema = etree.DTD(str(schema_path))
    except (etree.XMLSchemaParseError, etree.RelaxNGParseError,
            etree.DTDParseError, etree.XMLSyntaxError) as e:
        die(f"schema load error: {e}", code=EXIT_INPUT, as_json=as_json)

    valid = schema.validate(doc)
    errors = []
    if not valid:
        log = schema.error_log
        items = list(log) if all_errors else ([log[0]] if len(log) else [])
        for err in items:
            errors.append({
                "line": err.line, "column": err.column,
                "domain": err.domain_name, "type": err.type_name,
                "message": err.message,
            })

    if as_json:
        emit_json({"valid": valid, "errors": errors})
    elif valid:
        if not quiet:
            click.echo(f"valid: {src}")
    else:
        for e in errors:
            click.echo(f"{e['line']}:{e['column']} {e['message']}", err=True)

    if not valid:
        sys.exit(6)
