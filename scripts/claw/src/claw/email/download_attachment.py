"""claw email download-attachment — save a Gmail attachment to disk."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_SYSTEM, common_output_options, die, emit_json, gws_run, safe_write,
)


@click.command(name="download-attachment")
@click.argument("msg_id")
@click.argument("att_id")
@click.option("--out", "out", required=True, type=click.Path(path_type=Path))
@click.option("--verify-hash", default=None, help="SHA-256 of decoded bytes to verify.")
@common_output_options
def download_attachment(msg_id, att_id, out, verify_hash,
                        force, backup, as_json, dry_run, quiet, verbose, mkdir) -> None:
    """Fetch attachment <att-id> of <msg-id> → OUT."""
    if dry_run:
        click.echo(f"would fetch message={msg_id} attachment={att_id} → {out}")
        return

    try:
        proc = gws_run("gmail", "users", "messages", "attachments", "get",
                       "--params", json.dumps({
                           "userId": "me", "messageId": msg_id, "id": att_id,
                       }))
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, as_json=as_json)

    if proc.returncode != 0:
        die(f"gws attachments get failed: {proc.stderr.strip()}",
            code=EXIT_SYSTEM, as_json=as_json)

    data = json.loads(proc.stdout)
    b64 = data.get("data", "")
    if not b64:
        die("no attachment data returned", code=EXIT_INPUT, as_json=as_json)

    raw = base64.urlsafe_b64decode(b64 + "==")

    if verify_hash:
        got = hashlib.sha256(raw).hexdigest()
        if got.lower() != verify_hash.lower():
            die(f"hash mismatch: got {got}, expected {verify_hash}",
                code=EXIT_INPUT, as_json=as_json)

    def _writer(f) -> None:
        f.write(raw)

    try:
        safe_write(out, _writer, force=force, backup=backup, mkdir=mkdir)
    except FileExistsError as e:
        die(str(e), code=EXIT_INPUT, as_json=as_json)

    if as_json:
        emit_json({"path": str(out), "bytes": len(raw), "size": data.get("size")})
    elif not quiet:
        click.echo(f"wrote {out} ({len(raw)} bytes)")
