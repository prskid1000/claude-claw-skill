"""claw sheet — Google Drive upload/download wrapper. See references/claw/sheet.md."""

import click

from claw.common import LazyGroup

VERBS: dict[str, tuple[str, str]] = {
    "upload":   ("claw.sheet.upload", "upload"),
    "download": ("claw.sheet.download", "download"),
    "share":    ("claw.sheet.share", "share"),
    "list":     ("claw.sheet.list_", "list_"),
}


@click.command(cls=LazyGroup, lazy_commands=VERBS,
               context_settings={"help_option_names": ["-h", "--help"]})
def group() -> None:
    """Google Drive uploads/downloads — xlsx→Sheet/docx→Doc auto-convert."""
