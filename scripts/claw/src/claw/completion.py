"""claw completion — shell completion script emitter. See references/claw/completion.md."""

from __future__ import annotations

import os

import click


@click.command()
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish", "pwsh"]))
def completion(shell: str) -> None:
    """Emit a source-able completion script for the given shell.

    Examples:

        claw completion bash >> ~/.bashrc
        claw completion zsh  >> ~/.zshrc
        claw completion pwsh >> $PROFILE
    """
    os.environ["_CLAW_COMPLETE"] = f"{shell}_source"
    from claw.__main__ import cli  # noqa
    # Click internally emits the script when _CLAW_COMPLETE is set; fall through
    # by invoking cli() with no args — it will print and exit.
    try:
        cli.main(prog_name="claw", args=[], standalone_mode=True)
    except SystemExit:
        pass
