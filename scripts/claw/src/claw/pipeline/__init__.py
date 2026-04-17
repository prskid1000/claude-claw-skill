"""claw pipeline — YAML recipe runner. See references/claw/pipeline.md."""

import click

from claw.common import LazyGroup

VERBS: dict[str, tuple[str, str]] = {
    "run":         ("claw.pipeline.run", "run"),
    "validate":    ("claw.pipeline.validate", "validate"),
    "list-steps":  ("claw.pipeline.list_steps", "list_steps"),
    "graph":       ("claw.pipeline.graph", "graph"),
}


@click.command(cls=LazyGroup, lazy_commands=VERBS,
               context_settings={"help_option_names": ["-h", "--help"]})
def group() -> None:
    """YAML pipeline runner — DAG with ${step.out}, content-hash cache, retries."""
