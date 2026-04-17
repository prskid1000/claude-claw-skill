"""claw pipeline run — execute a YAML recipe as a DAG."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from typing import Any

import click

from claw.common import (
    EXIT_INPUT, EXIT_PARTIAL, EXIT_SYSTEM, EXIT_USAGE,
    common_output_options, die, emit_json,
)


_INTERP = re.compile(r"\$\{([^}]+)\}")


def _cache_root() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    p = Path(base) / "claw" / "pipeline"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_ref(ref: str, ctx: dict[str, Any]) -> str:
    ref = ref.strip()
    if ref.startswith("env:"):
        name_default = ref[4:]
        if ":-" in name_default:
            name, default = name_default.split(":-", 1)
        else:
            name, default = name_default, None
        val = os.environ.get(name.strip())
        if val is None:
            if default is None:
                raise KeyError(f"env var {name} not set")
            return default
        return val
    if ref.startswith("file:"):
        p = Path(ref[5:].strip()).expanduser()
        return p.read_text(encoding="utf-8")
    if ref.startswith("vars."):
        key = ref[5:]
        if key not in ctx.get("vars", {}):
            raise KeyError(f"unknown var: {key}")
        return str(ctx["vars"][key])
    if "." in ref:
        step_id, field = ref.split(".", 1)
        step_out = ctx.get("steps", {}).get(step_id)
        if step_out is None:
            raise KeyError(f"step {step_id!r} has no output yet")
        if field in step_out:
            return str(step_out[field])
        raise KeyError(f"step {step_id} has no field {field}")
    raise KeyError(f"cannot resolve ${{{ref}}}")


def _interpolate(value: Any, ctx: dict[str, Any]) -> Any:
    if isinstance(value, str):
        def sub(m: re.Match) -> str:
            return _resolve_ref(m.group(1), ctx)
        return _INTERP.sub(sub, value)
    if isinstance(value, list):
        return [_interpolate(v, ctx) for v in value]
    if isinstance(value, dict):
        return {k: _interpolate(v, ctx) for k, v in value.items()}
    return value


def _args_to_cli(args: dict[str, Any]) -> list[str]:
    cli: list[str] = []
    for k, v in args.items():
        flag = f"--{k.replace('_', '-')}"
        if isinstance(v, bool):
            if v:
                cli.append(flag)
        elif isinstance(v, list):
            for item in v:
                cli.extend([flag, str(item)])
        elif v is None:
            continue
        else:
            cli.extend([flag, str(v)])
    return cli


def _step_cache_key(step: dict, resolved_args: dict, recipe_name: str) -> str:
    h = hashlib.sha256()
    h.update(recipe_name.encode())
    h.update(b"\0")
    h.update(step["run"].encode())
    h.update(b"\0")
    h.update(json.dumps(resolved_args, sort_keys=True, default=str).encode())
    for key in sorted(resolved_args):
        val = resolved_args[key]
        if isinstance(val, str) and Path(val).is_file():
            h.update(f"\0file:{key}:{_sha256_file(Path(val))}".encode())
    return h.hexdigest()


def _emit_progress(fp, event: str, **fields) -> None:
    fp.write(json.dumps({"event": event, "ts": time.time(), **fields}) + "\n")
    fp.flush()


def _run_step(step: dict, ctx: dict, recipe_name: str, dry_run: bool,
              progress_fp, verbose: bool) -> tuple[int, dict]:
    step_id = step["id"]
    resolved_args = _interpolate(step.get("args", {}) or {}, ctx)
    cache_enabled = step.get("cache", True) is not False and step["run"] not in ("shell", "python")
    cache_key = _step_cache_key(step, resolved_args, recipe_name) if cache_enabled else None
    cache_dir = _cache_root() / cache_key[:2] / cache_key if cache_key else None
    if cache_dir and (cache_dir / "record.json").exists() and ctx.get("resume"):
        _emit_progress(progress_fp, "step_skip_cached", id=step_id)
        record = json.loads((cache_dir / "record.json").read_text())
        return 0, record

    run_spec = step["run"]
    if run_spec == "shell":
        cmd = resolved_args["cmd"]
        _emit_progress(progress_fp, "step_start", id=step_id, cmd=cmd)
        if dry_run:
            return 0, {"dry_run": True}
        start = time.monotonic()
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              cwd=resolved_args.get("cwd"),
                              input=resolved_args.get("stdin", ""))
        dur = int((time.monotonic() - start) * 1000)
        record = {"exit_code": proc.returncode, "stdout": proc.stdout,
                  "stderr": proc.stderr, "duration_ms": dur}
        rc = proc.returncode
    elif run_spec == "python":
        _emit_progress(progress_fp, "step_start", id=step_id)
        if dry_run:
            return 0, {"dry_run": True}
        start = time.monotonic()
        proc = subprocess.run([sys.executable, "-c", resolved_args["code"]],
                              input=resolved_args.get("stdin", ""),
                              capture_output=True, text=True)
        dur = int((time.monotonic() - start) * 1000)
        record = {"exit_code": proc.returncode, "stdout": proc.stdout,
                  "stderr": proc.stderr, "duration_ms": dur}
        rc = proc.returncode
    else:
        if "." not in run_spec:
            return 2, {"error": f"bad run spec: {run_spec}"}
        noun, verb = run_spec.split(".", 1)
        cmd = [sys.executable, "-m", "claw", noun, verb, *_args_to_cli(resolved_args), "--json"]
        _emit_progress(progress_fp, "step_start", id=step_id, cmd=cmd)
        if dry_run:
            return 0, {"dry_run": True, "cmd": cmd}

        retries = step.get("retries", 0)
        backoff = step.get("backoff", "exponential")
        attempt = 0
        start = time.monotonic()
        while True:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0 or attempt >= retries or proc.returncode == 2:
                break
            sleep = {"none": 0, "linear": attempt + 1,
                     "exponential": min(2 ** attempt, 30)}.get(backoff, 2 ** attempt)
            time.sleep(sleep)
            attempt += 1
        dur = int((time.monotonic() - start) * 1000)
        try:
            record = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
        except (json.JSONDecodeError, IndexError):
            record = {"stdout": proc.stdout}
        record.setdefault("stdout", proc.stdout)
        record["exit_code"] = proc.returncode
        record["duration_ms"] = dur
        rc = proc.returncode

    if rc == 0:
        _emit_progress(progress_fp, "step_success", id=step_id, duration_ms=record.get("duration_ms"))
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / "record.json").write_text(json.dumps(record))
    else:
        _emit_progress(progress_fp, "step_fail", id=step_id, exit_code=rc)
    return rc, record


@click.command(name="run")
@click.argument("recipe", type=click.Path(path_type=Path, exists=True))
@click.option("--jobs", default=None, type=int, help="Max parallel workers (default: cpu_count).")
@click.option("--resume", is_flag=True, help="Skip cache-hit steps.")
@click.option("--from", "from_step", default=None)
@click.option("--until", "until_step", default=None)
@click.option("--var", "var_overrides", multiple=True, metavar="K=V")
@click.option("--progress", type=click.Choice(["auto", "json"]), default="auto")
@common_output_options
def run(recipe: Path, jobs: int | None, resume: bool, from_step: str | None,
        until_step: str | None, var_overrides: tuple[str, ...], progress: str,
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Run a YAML pipeline recipe as a DAG."""
    try:
        import yaml
        import networkx as nx
    except ImportError:
        die("pyyaml / networkx not installed", code=EXIT_INPUT,
            hint="pip install 'claw[pipeline]'", as_json=as_json)

    try:
        recipe_data = yaml.safe_load(recipe.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        die(f"YAML parse error: {e}", code=EXIT_INPUT, as_json=as_json)

    name = recipe_data.get("name") or recipe.stem
    vars_map: dict[str, Any] = dict(recipe_data.get("vars") or {})
    for ov in var_overrides:
        if "=" not in ov:
            die(f"bad --var {ov!r}", code=EXIT_USAGE, as_json=as_json)
        k, v = ov.split("=", 1)
        vars_map[k.strip()] = v

    steps = recipe_data.get("steps") or []
    step_map = {s["id"]: s for s in steps}

    g = nx.DiGraph()
    for s in steps:
        g.add_node(s["id"])
        for dep in s.get("needs", []) or []:
            g.add_edge(dep, s["id"])
    if not nx.is_directed_acyclic_graph(g):
        die("pipeline has a cycle", code=EXIT_USAGE, as_json=as_json)

    if from_step:
        keep = nx.descendants(g, from_step) | {from_step}
        ancestors_needed = set()
        for n in keep:
            ancestors_needed |= nx.ancestors(g, n)
        keep |= ancestors_needed
        g = g.subgraph(keep).copy()
    if until_step:
        keep = nx.ancestors(g, until_step) | {until_step}
        g = g.subgraph(keep).copy()

    topo = list(nx.topological_sort(g))
    ctx: dict[str, Any] = {"vars": vars_map, "steps": {}, "resume": resume}

    progress_fp = sys.stderr
    if dry_run:
        click.echo("[plan]")
        for level, nodes in enumerate(nx.topological_generations(g), 1):
            click.echo(f"  wave {level}: {', '.join(nodes)}")
        click.echo(f"[vars] {vars_map}")
        if as_json:
            emit_json({"plan": topo, "vars": vars_map})
        return

    max_workers = jobs or os.cpu_count() or 1
    executor = ThreadPoolExecutor(max_workers=max_workers)
    remaining = set(topo)
    running: dict[str, Future] = {}
    failed: set[str] = set()
    skipped: set[str] = set()
    overall_exit = 0

    try:
        while remaining or running:
            ready = [n for n in list(remaining)
                     if n not in running
                     and all(pred in ctx["steps"] or pred in failed or pred in skipped
                             for pred in g.predecessors(n))]
            for n in ready:
                step = step_map[n]
                deps_failed = any(p in failed for p in g.predecessors(n))
                if deps_failed and step.get("on-error", "stop") != "continue":
                    skipped.add(n)
                    remaining.discard(n)
                    _emit_progress(progress_fp, "step_skip_dep_failed", id=n)
                    continue
                remaining.discard(n)
                fut = executor.submit(_run_step, step, ctx, name, False, progress_fp, verbose)
                running[n] = fut

            if not running:
                break
            done_now = [n for n, f in list(running.items()) if f.done()]
            if not done_now:
                next(iter(running.values())).result()
                continue
            for n in done_now:
                rc, record = running.pop(n).result()
                step = step_map[n]
                if rc == 0:
                    ctx["steps"][n] = record
                else:
                    policy = step.get("on-error", "stop")
                    overall_exit = max(overall_exit, rc if rc else 1)
                    if policy == "stop":
                        failed.add(n)
                        remaining.clear()
                        break
                    elif policy == "skip":
                        failed.add(n)
                        overall_exit = max(overall_exit, EXIT_PARTIAL)
                    elif policy == "continue":
                        ctx["steps"][n] = record
                        overall_exit = max(overall_exit, EXIT_PARTIAL)
    finally:
        executor.shutdown(wait=True)

    _emit_progress(progress_fp, "pipeline_done", exit_code=overall_exit,
                   succeeded=len(ctx["steps"]), failed=len(failed))
    if as_json:
        emit_json({"exit_code": overall_exit, "steps": {k: ctx["steps"].get(k) for k in topo},
                   "failed": sorted(failed)})
    sys.exit(overall_exit)
