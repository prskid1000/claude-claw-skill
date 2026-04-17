"""claw pdf info — metadata + structural summary."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import die, emit_json


@click.command(name="info")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--json", "as_json", is_flag=True)
def info(src: Path, as_json: bool) -> None:
    """Print metadata + structural summary of <SRC>."""
    try:
        import fitz
    except ImportError:
        die("PyMuPDF not installed; install: pip install 'claw[pdf]'")

    stat = src.stat()
    doc = fitz.open(str(src))
    try:
        meta = dict(doc.metadata or {})
        has_text_heuristic = False
        for i in range(min(3, doc.page_count)):
            if doc.load_page(i).get_text("text").strip():
                has_text_heuristic = True
                break

        try:
            layers = [ocg.get("name", "?") for ocg in (doc.layer_ui_configs() or [])]
        except Exception:
            layers = []
        try:
            attachments = doc.embfile_names() if hasattr(doc, "embfile_names") else []
        except Exception:
            attachments = []

        payload = {
            "path": str(src),
            "size_bytes": stat.st_size,
            "page_count": doc.page_count,
            "encrypted": bool(doc.is_encrypted),
            "needs_password": bool(doc.needs_pass),
            "permissions": int(doc.permissions) if doc.is_encrypted else None,
            "pdf_version": getattr(doc, "pdf_version", lambda: None)()
                if callable(getattr(doc, "pdf_version", None)) else None,
            "has_form": bool(doc.is_form_pdf) if hasattr(doc, "is_form_pdf") else False,
            "has_text_layer_heuristic": has_text_heuristic,
            "layers": layers,
            "attachments": list(attachments),
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "keywords": meta.get("keywords", ""),
            "creator": meta.get("creator", ""),
            "producer": meta.get("producer", ""),
            "creation_date": meta.get("creationDate", ""),
            "mod_date": meta.get("modDate", ""),
        }
    finally:
        doc.close()

    if as_json:
        emit_json(payload)
        return

    click.echo(f"File:        {payload['path']}")
    click.echo(f"Size:        {payload['size_bytes']:,} bytes")
    click.echo(f"Pages:       {payload['page_count']}")
    click.echo(f"Encrypted:   {payload['encrypted']}")
    if payload["pdf_version"]:
        click.echo(f"PDF version: {payload['pdf_version']}")
    click.echo(f"Has form:    {payload['has_form']}")
    click.echo(f"Has text:    {payload['has_text_layer_heuristic']}")
    click.echo(f"Layers:      {', '.join(payload['layers']) or '(none)'}")
    click.echo(f"Attachments: {len(payload['attachments'])}")
    click.echo("── Metadata ──")
    for k in ("title", "author", "subject", "keywords", "creator", "producer",
              "creation_date", "mod_date"):
        v = payload[k]
        if v:
            click.echo(f"  {k:14s} {v}")
