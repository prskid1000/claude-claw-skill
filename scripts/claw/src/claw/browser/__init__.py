"""claw browser — Chromium launcher. See references/claw/browser.md."""

import click

from claw.common import LazyGroup

VERBS: dict[str, tuple[str, str]] = {
    "launch": ("claw.browser.launch", "launch"),
}


@click.command(cls=LazyGroup, lazy_commands=VERBS,
               context_settings={"help_option_names": ["-h", "--help"]})
def group() -> None:
    """Chromium launcher for Chrome DevTools MCP debug-protocol."""
