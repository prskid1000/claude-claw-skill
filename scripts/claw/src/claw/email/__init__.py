"""claw email — MIME compose + Gmail wrapper. See references/claw/email.md."""

import click

from claw.common import LazyGroup

VERBS: dict[str, tuple[str, str]] = {
    "send":                ("claw.email.send", "send"),
    "reply":               ("claw.email.reply", "reply"),
    "forward":             ("claw.email.forward", "forward"),
    "draft":               ("claw.email.draft", "draft"),
    "search":              ("claw.email.search", "search"),
    "download-attachment": ("claw.email.download_attachment", "download_attachment"),
}


@click.command(cls=LazyGroup, lazy_commands=VERBS,
               context_settings={"help_option_names": ["-h", "--help"]})
def group() -> None:
    """Email — send, reply, forward, draft, search (Gmail API + MIME)."""
