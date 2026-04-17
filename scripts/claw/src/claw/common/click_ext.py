"""Click helpers: LazyGroup for fast --help, common_output_options decorator."""

from __future__ import annotations

import importlib
from typing import Any, Callable

import click


class LazyGroup(click.Group):
    """A click.Group that defers importing subcommand modules until invoked.

    lazy_commands: {verb_name: (module_path, attr_name)}
    """

    def __init__(self, *args: Any, lazy_commands: dict[str, tuple[str, str]] | None = None,
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._lazy: dict[str, tuple[str, str]] = dict(lazy_commands or {})

    def list_commands(self, ctx: click.Context) -> list[str]:
        names = set(super().list_commands(ctx)) | set(self._lazy.keys())
        return sorted(names)

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        if cmd_name in self._lazy:
            mod_path, attr = self._lazy[cmd_name]
            try:
                mod = importlib.import_module(mod_path)
            except ImportError as e:
                raise click.ClickException(f"failed to load {cmd_name}: {e}") from e
            cmd = getattr(mod, attr, None)
            if cmd is None:
                raise click.ClickException(f"module {mod_path} missing attribute {attr!r}")
            return cmd
        return super().get_command(ctx, cmd_name)


def common_output_options(f: Callable) -> Callable:
    """Decorator adding --force --backup --json --dry-run --quiet -v --mkdir."""
    f = click.option("--mkdir", is_flag=True, help="Create parent directories as needed.")(f)
    f = click.option("-v", "--verbose", is_flag=True, help="Verbose output.")(f)
    f = click.option("-q", "--quiet", is_flag=True, help="Suppress non-error output.")(f)
    f = click.option("--dry-run", "dry_run", is_flag=True, help="Show plan without writing.")(f)
    f = click.option("--json", "as_json", is_flag=True, help="Emit JSON summary on stdout.")(f)
    f = click.option("--backup", is_flag=True, help="Write .bak sidecar before overwriting.")(f)
    f = click.option("--force", is_flag=True, help="Overwrite existing output.")(f)
    return f


def help_all_option() -> Callable:
    """Adds `--help-all` that walks all subcommands and prints their help."""

    def decorator(f: Callable) -> Callable:
        def _cb(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
            if not value or ctx.resilient_parsing:
                return
            cmd = ctx.command
            click.echo(ctx.get_help())
            if isinstance(cmd, click.Group):
                for name in cmd.list_commands(ctx):
                    sub = cmd.get_command(ctx, name)
                    if sub is None:
                        continue
                    click.echo("\n" + "=" * 60)
                    click.echo(f"claw {name}")
                    click.echo("=" * 60)
                    sub_ctx = click.Context(sub, info_name=name, parent=ctx)
                    click.echo(sub.get_help(sub_ctx))
            ctx.exit()

        return click.option("--help-all", is_flag=True, expose_value=False,
                            is_eager=True, callback=_cb,
                            help="Show help for all subcommands.")(f)

    return decorator
