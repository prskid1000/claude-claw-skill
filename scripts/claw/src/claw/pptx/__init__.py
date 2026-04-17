"""claw pptx — PowerPoint operations. See references/claw/pptx.md."""

import click

from claw.common import LazyGroup

VERBS: dict[str, tuple[str, str]] = {
    "new":         ("claw.pptx.new", "new"),
    "add-slide":   ("claw.pptx.add_slide", "add_slide"),
    "add-chart":   ("claw.pptx.add_chart", "add_chart"),
    "add-table":   ("claw.pptx.add_table", "add_table"),
    "add-image":   ("claw.pptx.add_image", "add_image"),
    "notes":       ("claw.pptx.notes", "notes"),
    "meta":        ("claw.pptx.meta", "meta"),
}


@click.command(cls=LazyGroup, lazy_commands=VERBS,
               context_settings={"help_option_names": ["-h", "--help"]})
def group() -> None:
    """PowerPoint (.pptx) — new, add-slide/chart/table/image, notes, meta."""
