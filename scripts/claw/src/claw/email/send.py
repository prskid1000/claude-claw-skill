"""claw email send — compose + Gmail API send."""

from __future__ import annotations

import json
import sys

import click

from claw.common import EXIT_INPUT, EXIT_SYSTEM, common_output_options, die, emit_json, gws_run, read_text

from claw.email._mime import _parse_addrs, build_message, to_raw_b64


@click.command(name="send")
@click.option("--to", "to", multiple=True, required=True, help="Recipient; repeatable.")
@click.option("--cc", multiple=True)
@click.option("--bcc", multiple=True)
@click.option("--subject", required=True)
@click.option("--body", "body_text", default=None, help="Literal plain-text body.")
@click.option("--body-file", default=None, type=click.Path(exists=True, dir_okay=False))
@click.option("--body-stdin", is_flag=True, help="Read plain body from stdin.")
@click.option("--html", default=None, type=click.Path(exists=True, dir_okay=False),
              help="HTML alternative body file.")
@click.option("--attach", "attachments", multiple=True, help="@path[:mime/type]; repeatable.")
@click.option("--inline", "inline", multiple=True, help="CID=@path; inline image refs.")
@click.option("--from", "from_addr", default=None)
@click.option("--reply-to", default=None)
@click.option("--header", "headers", multiple=True, help="KEY=VALUE; repeatable.")
@common_output_options
def send(to, cc, bcc, subject, body_text, body_file, body_stdin, html,
         attachments, inline, from_addr, reply_to, headers,
         force, backup, as_json, dry_run, quiet, verbose, mkdir) -> None:
    """Send a new email via Gmail API (MIME composed locally)."""
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
        preview = msg.as_string()
        if len(preview) > 2048:
            preview = preview[:2048] + "\n... [truncated]"
        if as_json:
            emit_json({"dry_run": True, "headers": dict(msg.items()),
                       "raw_bytes": len(raw_b64), "body_preview": preview})
        else:
            click.echo(preview)
        return

    try:
        proc = gws_run("gmail", "users", "messages", "send",
                       "--params", json.dumps({"userId": "me"}),
                       "--json", json.dumps({"raw": raw_b64}))
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, as_json=as_json)

    if proc.returncode != 0:
        die(f"gws send failed: {proc.stderr.strip()}", code=EXIT_SYSTEM, as_json=as_json)

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = {"raw": proc.stdout.strip()}
    if as_json:
        emit_json(data)
    elif not quiet:
        click.echo(f"sent id={data.get('id', '?')} thread={data.get('threadId', '?')}")
