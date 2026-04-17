"""claw doc create — create a Google Doc, optionally populate from markdown."""

from __future__ import annotations

import json

import click

from claw.common import EXIT_SYSTEM, common_output_options, die, emit_json, gws_run


@click.command(name="create")
@click.option("--title", required=True)
@click.option("--from", "source", default=None, type=click.Path(exists=True, dir_okay=False),
              help="Markdown file to populate the new doc from.")
@click.option("--parent", default=None, help="Drive folder ID.")
@click.option("--share", "shares", multiple=True,
              help="ACL spec: user:EMAIL:role | domain:DOMAIN:role | anyone:role")
@click.option("--tab", "tab_id", default=None)
@common_output_options
def create(title, source, parent, shares, tab_id,
           force, backup, as_json, dry_run, quiet, verbose, mkdir) -> None:
    """Create a new Google Doc."""
    if dry_run:
        click.echo(f"would create doc title={title!r} parent={parent} share={list(shares)}")
        return

    try:
        proc = gws_run("docs", "documents", "create",
                       "--json", json.dumps({"title": title}))
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, as_json=as_json)
    if proc.returncode != 0:
        die(f"gws docs create failed: {proc.stderr.strip()}",
            code=EXIT_SYSTEM, as_json=as_json)

    doc = json.loads(proc.stdout)
    doc_id = doc.get("documentId")

    if parent:
        mv = gws_run("drive", "files", "update",
                     "--params", json.dumps({"fileId": doc_id, "addParents": parent}),
                     "--json", json.dumps({}))
        if mv.returncode != 0 and verbose:
            click.echo(f"move warning: {mv.stderr.strip()}", err=True)

    for spec in shares:
        payload = _parse_share(spec)
        if payload is None:
            click.echo(f"bad --share: {spec}", err=True)
            continue
        params = {"fileId": doc_id}
        if payload.get("role") == "owner":
            params["transferOwnership"] = True
        sh = gws_run("drive", "permissions", "create",
                     "--params", json.dumps(params),
                     "--json", json.dumps(payload))
        if sh.returncode != 0 and verbose:
            click.echo(f"share warning: {sh.stderr.strip()}", err=True)

    if source:
        from claw.doc.build import _build_and_dispatch  # late import
        _build_and_dispatch(doc_id, source, tab_id or "t.0",
                            append=False, chunk_size=8, from_index=0,
                            as_json=as_json, quiet=quiet, verbose=verbose)

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    if as_json:
        emit_json({"doc_id": doc_id, "revision_id": doc.get("revisionId"), "url": url})
    elif not quiet:
        click.echo(f"created {doc_id} → {url}")


def _parse_share(spec: str) -> dict | None:
    parts = spec.split(":")
    if parts[0] == "user" and len(parts) == 3:
        return {"role": parts[2], "type": "user", "emailAddress": parts[1]}
    if parts[0] == "domain" and len(parts) == 3:
        return {"role": parts[2], "type": "domain", "domain": parts[1]}
    if parts[0] == "anyone" and len(parts) == 2:
        return {"role": parts[1], "type": "anyone"}
    return None
