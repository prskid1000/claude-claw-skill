"""claw email search — Gmail query → NDJSON / table."""

from __future__ import annotations

import json

import click

from claw.common import EXIT_SYSTEM, common_output_options, die, emit_json, gws_run


def _fetch_msg(msg_id: str, fmt: str) -> dict:
    proc = gws_run("gmail", "users", "messages", "get",
                   "--params", json.dumps({"userId": "me", "id": msg_id, "format": fmt}))
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip())
    return json.loads(proc.stdout)


def _headers_of(msg: dict) -> dict[str, str]:
    return {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}


@click.command(name="search")
@click.option("--q", "query", required=True, help="Gmail search operators.")
@click.option("--max", "max_results", default=25, type=int)
@click.option("--format", "fmt", type=click.Choice(["table", "json", "full"]), default="table")
@click.option("--include-spam-trash", is_flag=True)
@click.option("--label", default=None, help="Shortcut for label:L added to query.")
@common_output_options
def search(query, max_results, fmt, include_spam_trash, label,
           force, backup, as_json, dry_run, quiet, verbose, mkdir) -> None:
    """Search the mailbox via Gmail query syntax."""
    q = query
    if label:
        q = f"{q} label:{label}".strip()

    params = {"userId": "me", "q": q, "maxResults": max_results}
    if include_spam_trash:
        params["includeSpamTrash"] = True

    try:
        proc = gws_run("gmail", "users", "messages", "list",
                       "--params", json.dumps(params))
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, as_json=as_json)

    if proc.returncode != 0:
        die(f"gws list failed: {proc.stderr.strip()}", code=EXIT_SYSTEM, as_json=as_json)

    data = json.loads(proc.stdout or "{}")
    ids = [m["id"] for m in data.get("messages", [])][:max_results]

    detail_format = "full" if fmt == "full" else "metadata"
    records: list[dict] = []
    for mid in ids:
        try:
            msg = _fetch_msg(mid, detail_format)
        except RuntimeError as e:
            if verbose:
                click.echo(f"skip {mid}: {e}", err=True)
            continue
        hdrs = _headers_of(msg)
        rec = {
            "id": msg.get("id"),
            "threadId": msg.get("threadId"),
            "from": hdrs.get("From", ""),
            "to": hdrs.get("To", ""),
            "subject": hdrs.get("Subject", ""),
            "date": hdrs.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        }
        if fmt == "full":
            rec["payload"] = msg.get("payload")
            rec["labelIds"] = msg.get("labelIds")
        records.append(rec)

    if fmt == "json" or fmt == "full" or as_json:
        for r in records:
            emit_json(r)
        return

    for r in records:
        click.echo(f"{r['id']}  {r['from'][:30]:30}  {r['subject'][:60]}")
