"""claw pipeline list-steps — enumerate available step types."""
from __future__ import annotations

import importlib
from pathlib import Path

import click

from claw.common import common_output_options, emit_json


def _discover() -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    pkg_root = Path(__file__).resolve().parent.parent
    for child in sorted(pkg_root.iterdir()):
        if not child.is_dir() or not (child / "__init__.py").exists():
            continue
        if child.name in ("common", "pipeline", "__pycache__"):
            continue
        mod_name = f"claw.{child.name}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        verbs = getattr(mod, "VERBS", None)
        if isinstance(verbs, dict):
            for verb in sorted(verbs):
                results.append((f"{child.name}.{verb}", f"claw {child.name} {verb}"))
    results.extend([("shell", "<raw command>"), ("python", "<inline python>")])
    return results


@click.command(name="list-steps")
@common_output_options
def list_steps(force: bool, backup: bool, as_json: bool, dry_run: bool,
               quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Enumerate every step type the runner understands."""
    entries = _discover()
    if as_json:
        for run_spec, cli in entries:
            emit_json({"run": run_spec, "claw": cli})
        return
    width = max((len(r) for r, _ in entries), default=10)
    for run_spec, cli in entries:
        click.echo(f"{run_spec.ljust(width)}  {cli}")
