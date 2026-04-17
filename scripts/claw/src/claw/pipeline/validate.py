"""claw pipeline validate — static checks on a recipe."""
from __future__ import annotations

import importlib
import os
import re
import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, EXIT_USAGE, common_output_options, die, emit_json,
)


_INTERP = re.compile(r"\$\{([^}]+)\}")
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def _known_step_types() -> set[str]:
    types: set[str] = {"shell", "python"}
    pkg_root = Path(__file__).resolve().parent.parent
    for child in pkg_root.iterdir():
        if not child.is_dir() or not (child / "__init__.py").exists():
            continue
        mod_name = f"claw.{child.name}"
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        verbs = getattr(mod, "VERBS", None)
        if isinstance(verbs, dict):
            for v in verbs:
                types.add(f"{child.name}.{v}")
    return types


def _collect_refs(value) -> list[str]:
    if isinstance(value, str):
        return _INTERP.findall(value)
    if isinstance(value, list):
        out = []
        for v in value:
            out.extend(_collect_refs(v))
        return out
    if isinstance(value, dict):
        out = []
        for v in value.values():
            out.extend(_collect_refs(v))
        return out
    return []


@click.command(name="validate")
@click.argument("recipe", type=click.Path(path_type=Path, exists=True))
@common_output_options
def validate(recipe: Path, force: bool, backup: bool, as_json: bool, dry_run: bool,
             quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Statically validate a pipeline recipe."""
    try:
        import yaml
        import networkx as nx
    except ImportError:
        die("pyyaml / networkx not installed", code=EXIT_INPUT,
            hint="pip install 'claw[pipeline]'", as_json=as_json)

    try:
        data = yaml.safe_load(recipe.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        die(f"YAML parse error: {e}", code=EXIT_INPUT, as_json=as_json)

    errors: list[dict] = []

    if not isinstance(data, dict):
        die("recipe must be a mapping", code=EXIT_INPUT, as_json=as_json)
    if not data.get("name"):
        errors.append({"path": "name", "rule": "required", "message": "top-level `name` is required"})
    steps = data.get("steps") or []
    if not isinstance(steps, list) or not steps:
        errors.append({"path": "steps", "rule": "required", "message": "`steps` must be a non-empty list"})

    ids: set[str] = set()
    vars_map = data.get("vars") or {}
    known_types = _known_step_types()

    g = nx.DiGraph()
    for i, step in enumerate(steps):
        prefix = f"steps[{i}]"
        sid = step.get("id")
        if not sid or not isinstance(sid, str) or not _ID_RE.match(sid):
            errors.append({"path": f"{prefix}.id", "rule": "format",
                           "message": f"bad id {sid!r} (need {_ID_RE.pattern})"})
            continue
        if sid in ids:
            errors.append({"path": f"{prefix}.id", "rule": "unique",
                           "message": f"duplicate step id {sid!r}"})
        ids.add(sid)
        g.add_node(sid)
        rtype = step.get("run")
        if not rtype:
            errors.append({"path": f"{prefix}.run", "rule": "required",
                           "message": "`run` is required"})
        elif rtype not in known_types:
            errors.append({"path": f"{prefix}.run", "rule": "unknown-step",
                           "message": f"unknown step type {rtype!r}",
                           "hint": "run `claw pipeline list-steps` to enumerate"})
        for dep in step.get("needs") or []:
            g.add_edge(dep, sid)

    for i, step in enumerate(steps):
        sid = step.get("id")
        for dep in step.get("needs") or []:
            if dep not in ids:
                errors.append({"path": f"steps[{i}].needs",
                               "rule": "unknown-ref",
                               "message": f"step {sid!r} needs unknown step {dep!r}"})

    if not nx.is_directed_acyclic_graph(g):
        try:
            cycle = nx.find_cycle(g)
            errors.append({"path": "steps", "rule": "cycle",
                           "message": f"cycle detected: {cycle}"})
        except nx.NetworkXNoCycle:
            pass

    for i, step in enumerate(steps):
        sid = step.get("id")
        refs = _collect_refs(step.get("args") or {})
        for ref in refs:
            target = ref.strip()
            if target.startswith(("env:", "file:")):
                continue
            if target.startswith("vars."):
                key = target[5:]
                if key not in vars_map:
                    errors.append({"path": f"steps[{i}].args",
                                   "rule": "unresolved-ref",
                                   "message": f"unknown var {key!r} in {sid!r}"})
            elif "." in target:
                dep_id = target.split(".", 1)[0]
                if dep_id not in ids:
                    errors.append({"path": f"steps[{i}].args",
                                   "rule": "unresolved-ref",
                                   "message": f"references unknown step {dep_id!r}"})
                elif dep_id not in (step.get("needs") or []):
                    errors.append({"path": f"steps[{i}].needs",
                                   "rule": "missing-needs",
                                   "message": f"uses ${{{target}}} but {dep_id!r} not in needs"})

    if as_json:
        emit_json({"valid": not errors, "errors": errors})
    else:
        if errors:
            for e in errors:
                click.echo(f"{e['path']}: {e['message']}", err=True)
        elif not quiet:
            click.echo(f"valid: {recipe}")

    sys.exit(EXIT_USAGE if errors else 0)
