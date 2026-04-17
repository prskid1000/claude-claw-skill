"""claw doc export — export a Doc via drive.files.export."""

from __future__ import annotations

import json
from pathlib import Path

import click

from claw.common import EXIT_INPUT, EXIT_SYSTEM, common_output_options, die, emit_json, gws_run


MIME_MAP = {
    "pdf":  "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "html": "text/html",
    "md":   "text/markdown",
    "txt":  "text/plain",
    "epub": "application/epub+zip",
    "odt":  "application/vnd.oasis.opendocument.text",
    "rtf":  "application/rtf",
}


@click.command(name="export")
@click.argument("doc_id")
@click.option("--as", "format_",
              type=click.Choice(list(MIME_MAP)), required=True)
@click.option("--out", required=True, type=click.Path(path_type=Path))
@common_output_options
def export(doc_id, format_, out,
           force, backup, as_json, dry_run, quiet, verbose, mkdir) -> None:
    """Export DOC_ID to OUT as --as pdf|docx|html|md|txt|epub."""
    fmt = format_
    mime = MIME_MAP[fmt]
    if out.exists() and not force:
        die(f"{out} exists (pass --force to overwrite)",
            code=EXIT_INPUT, as_json=as_json)
    if mkdir:
        out.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        click.echo(f"would export doc={doc_id} as={fmt} → {out}")
        return

    try:
        proc = gws_run("drive", "files", "export",
                       "--params", json.dumps({"fileId": doc_id, "mimeType": mime}),
                       "--output", str(out))
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, as_json=as_json)

    if proc.returncode != 0:
        die(f"gws export failed: {proc.stderr.strip()}",
            code=EXIT_SYSTEM, as_json=as_json)

    if as_json:
        emit_json({"doc_id": doc_id, "format": fmt, "path": str(out),
                   "bytes": out.stat().st_size if out.exists() else 0})
    elif not quiet:
        click.echo(f"exported {doc_id} → {out}")
