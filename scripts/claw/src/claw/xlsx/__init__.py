"""claw xlsx — Excel operations. See references/claw/xlsx.md."""

import click

from claw.common import LazyGroup

VERBS: dict[str, tuple[str, str]] = {
    "new":         ("claw.xlsx.new", "new"),
    "read":        ("claw.xlsx.read", "read"),
    "append":      ("claw.xlsx.append", "append"),
    "from-csv":    ("claw.xlsx.from_csv", "from_csv"),
    "from-json":   ("claw.xlsx.from_json", "from_json"),
    "to-csv":      ("claw.xlsx.to_csv", "to_csv"),
    "freeze":      ("claw.xlsx.freeze", "freeze"),
    "filter":      ("claw.xlsx.filter_", "filter_"),
    "chart":       ("claw.xlsx.chart", "chart"),
    "validate":    ("claw.xlsx.validate", "validate"),
    "protect":     ("claw.xlsx.protect", "protect"),
    "conditional": ("claw.xlsx.conditional", "conditional"),
    "meta":        ("claw.xlsx.meta", "meta"),
    "stat":        ("claw.xlsx.stat", "stat"),
}


@click.command(cls=LazyGroup, lazy_commands=VERBS,
               context_settings={"help_option_names": ["-h", "--help"]})
def group() -> None:
    """Excel (.xlsx) operations — new, read, chart, validate, protect, freeze, filter."""
