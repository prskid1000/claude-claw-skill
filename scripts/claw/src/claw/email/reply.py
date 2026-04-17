"""claw email reply — fetches thread headers, builds a correctly-threaded reply."""

from __future__ import annotations

import json
import sys

import click

from claw.common import EXIT_INPUT, EXIT_SYSTEM, common_output_options, die, emit_json, gws_run, read_text

from claw.email._mime import _parse_addrs, build_message, to_raw_b64


def _fetch_headers(msg_id: str) -> tuple[dict[str, str], str]:
    """Return (parsed headers dict, threadId)."""
    proc = gws_run("gmail", "users", "messages", "get",
                   "--params", json.dumps({
                       "userId": "me", "id": msg_id, "format": "metadata",
                       "metadataHeaders": ["From", "To", "Cc", "Subject",
                                           "Message-Id", "References", "In-Reply-To"],
                   }))
    if proc.returncode != 0:
        raise RuntimeError(f"gws get failed: {proc.stderr.strip()}")
    data = json.loads(proc.stdout)
    headers = {h["name"]: h["value"]
               for h in data.get("payload", {}).get("headers", [])}
    return headers, data.get("threadId", "")


def _derive_recipients(headers: dict[str, str], *, reply_all: bool,
                       remove: list[str], add_cc: list[str]) -> tuple[list[str], list[str]]:
    from_addr = headers.get("From", "")
    to_list = [from_addr] if from_addr else []
    cc_list: list[str] = []
    if reply_all:
        for v in (headers.get("To", ""), headers.get("Cc", "")):
            for part in v.split(","):
                part = part.strip()
                if part and part != from_addr:
                    cc_list.append(part)
    cc_list.extend(add_cc)
    rm = {r.strip().lower() for r in remove}
    to_list = [a for a in to_list if a.lower() not in rm and _email_from_header(a).lower() not in rm]
    cc_list = [a for a in cc_list if a.lower() not in rm and _email_from_header(a).lower() not in rm]
    return to_list, cc_list


def _email_from_header(h: str) -> str:
    if "<" in h and ">" in h:
        return h[h.index("<") + 1:h.index(">")]
    return h.strip()


@click.command(name="reply")
@click.argument("msg_id")
@click.option("--body", "body_text", default=None)
@click.option("--body-file", default=None, type=click.Path(exists=True, dir_okay=False))
@click.option("--body-stdin", is_flag=True)
@click.option("--all", "reply_all", is_flag=True, help="Reply-all.")
@click.option("--remove", multiple=True, help="Drop an address from To/Cc.")
@click.option("--add-cc", multiple=True, help="Additional Cc.")
@click.option("--html", default=None, type=click.Path(exists=True, dir_okay=False))
@click.option("--attach", "attachments", multiple=True)
@click.option("--inline", "inline", multiple=True)
@click.option("--subject", default=None)
@common_output_options
def reply(msg_id, body_text, body_file, body_stdin, reply_all, remove, add_cc,
          html, attachments, inline, subject,
          force, backup, as_json, dry_run, quiet, verbose, mkdir) -> None:
    """Reply to <msg-id>, preserving thread."""
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
        headers, thread_id = _fetch_headers(msg_id)
    except (RuntimeError, FileNotFoundError) as e:
        die(str(e), code=EXIT_SYSTEM, as_json=as_json)

    parent_msg_id = headers.get("Message-Id") or headers.get("Message-ID", "")
    refs = headers.get("References", "")
    new_refs = f"{refs} {parent_msg_id}".strip() if refs else parent_msg_id

    parent_subject = headers.get("Subject", "")
    final_subject = subject or (parent_subject if parent_subject.lower().startswith("re:")
                                else f"Re: {parent_subject}")

    to_list, cc_list = _derive_recipients(
        headers, reply_all=reply_all, remove=list(remove), add_cc=list(add_cc),
    )

    try:
        msg = build_message(
            to=to_list, cc=cc_list, bcc=[],
            subject=final_subject, body=body, html=html,
            attachments=list(attachments), inline=list(inline),
            in_reply_to=parent_msg_id, references=new_refs,
        )
    except (ValueError, FileNotFoundError) as e:
        die(str(e), code=EXIT_INPUT, as_json=as_json)

    raw_b64 = to_raw_b64(msg)

    if dry_run:
        if as_json:
            emit_json({"dry_run": True, "threadId": thread_id,
                       "headers": dict(msg.items())})
        else:
            click.echo(msg.as_string()[:2048])
        return

    proc = gws_run("gmail", "users", "messages", "send",
                   "--params", json.dumps({"userId": "me"}),
                   "--json", json.dumps({"raw": raw_b64, "threadId": thread_id}))
    if proc.returncode != 0:
        die(f"gws send failed: {proc.stderr.strip()}", code=EXIT_SYSTEM, as_json=as_json)

    data = json.loads(proc.stdout)
    if as_json:
        emit_json(data)
    elif not quiet:
        click.echo(f"replied id={data.get('id', '?')} thread={data.get('threadId', '?')}")
