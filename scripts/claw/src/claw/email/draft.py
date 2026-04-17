"""claw email draft — same flags as send, writes to Drafts."""

from __future__ import annotations

import json
import sys

import click

from claw.common import EXIT_INPUT, EXIT_SYSTEM, common_output_options, die, emit_json, gws_run, read_text

from claw.email._mime import _parse_addrs, build_message, to_raw_b64


@click.command(name="draft")
@click.option("--to", "to", multiple=True, required=True)
@click.option("--cc", multiple=True)
@click.option("--bcc", multiple=True)
@click.option("--subject", required=True)
@click.option("--body", "body_text", default=None)
@click.option("--body-file", default=None, type=click.Path(exists=True, dir_okay=False))
@click.option("--body-stdin", is_flag=True)
@click.option("--html", default=None, type=click.Path(exists=True, dir_okay=False))
@click.option("--attach", "attachments", multiple=True)
@click.option("--inline", "inline", multiple=True)
@click.option("--from", "from_addr", default=None)
@click.option("--reply-to", default=None)
@click.option("--header", "headers", multiple=True)
@common_output_options
def draft(to, cc, bcc, subject, body_text, body_file, body_stdin, html,
          attachments, inline, from_addr, reply_to, headers,
          force, backup, as_json, dry_run, quiet, verbose, mkdir) -> None:
    """Create a Gmail draft (same surface as `send`)."""
    if sum(bool(x) for x in (body_text, body_file, body_stdin)) != 1:
        die("exactly one of --body, --body-file, --body-stdin required",
            code=EXIT_INPUT, as_json=as_json)

    if body_stdin:
        body = sys.stdin.read()
    elif body_file:
        body = read_text(body_file)
    else:
        body = body_text or ""

    try:
        msg = build_message(
            to=_parse_addrs(to), cc=_parse_addrs(cc), bcc=_parse_addrs(bcc),
            subject=subject, body=body, html=html,
            attachments=list(attachments), inline=list(inline),
            from_addr=from_addr, reply_to=reply_to, headers=list(headers),
        )
    except (ValueError, FileNotFoundError) as e:
        die(str(e), code=EXIT_INPUT, as_json=as_json)

    raw_b64 = to_raw_b64(msg)

    if dry_run:
        if as_json:
            emit_json({"dry_run": True, "headers": dict(msg.items()), "raw_bytes": len(raw_b64)})
        else:
            click.echo(msg.as_string()[:2048])
        return

    try:
        proc = gws_run("gmail", "users", "drafts", "create",
                       "--params", json.dumps({"userId": "me"}),
                       "--json", json.dumps({"message": {"raw": raw_b64}}))
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, as_json=as_json)

    if proc.returncode != 0:
        die(f"gws drafts create failed: {proc.stderr.strip()}",
            code=EXIT_SYSTEM, as_json=as_json)

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = {"raw": proc.stdout.strip()}
    if as_json:
        emit_json(data)
    elif not quiet:
        click.echo(f"drafted id={data.get('id', '?')}")
