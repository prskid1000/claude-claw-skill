"""claw html — BeautifulSoup/lxml HTML wrapper. See references/claw/html.md."""

import click

from claw.common import LazyGroup

VERBS: dict[str, tuple[str, str]] = {
    "select":     ("claw.html.select", "select"),
    "text":       ("claw.html.text", "text"),
    "strip":      ("claw.html.strip", "strip_"),
    "sanitize":   ("claw.html.sanitize", "sanitize"),
    "absolutize": ("claw.html.absolutize", "absolutize"),
    "fmt":        ("claw.html.fmt", "fmt"),
}


@click.command(cls=LazyGroup, lazy_commands=VERBS,
               context_settings={"help_option_names": ["-h", "--help"]})
def group() -> None:
    """HTML — CSS select, text extract, strip, sanitize, absolutize."""
