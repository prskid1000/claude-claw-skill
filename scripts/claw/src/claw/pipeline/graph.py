"""claw pipeline graph — visualize the DAG as dot / mermaid / ascii."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, safe_write,
)


def _to_dot(edges: list[tuple[str, str]], nodes: list[str], name: str) -> str:
    lines = [f'digraph "{name}" {{']
    lines.append("  rankdir=LR;")
    for n in nodes:
        lines.append(f'  "{n}";')
    for a, b in edges:
        lines.append(f'  "{a}" -> "{b}";')
    lines.append("}")
    return "\n".join(lines) + "\n"


def _to_mermaid(edges: list[tuple[str, str]], nodes: list[str]) -> str:
    lines = ["```mermaid", "graph LR"]
    for n in nodes:
        lines.append(f"  {n}[{n}]")
    for a, b in edges:
        lines.append(f"  {a} --> {b}")
    lines.append("```")
    return "\n".join(lines) + "\n"


def _to_ascii(generations: list[list[str]], edges: list[tuple[str, str]]) -> str:
    out_lines: list[str] = []
    for i, gen in enumerate(generations):
        prefix = f"wave {i + 1}: "
        out_lines.append(prefix + ", ".join(gen))
    out_lines.append("")
    for a, b in edges:
        out_lines.append(f"  {a} -> {b}")
    return "\n".join(out_lines) + "\n"


@click.command(name="graph")
@click.argument("recipe", type=click.Path(path_type=Path, exists=True))
@click.option("--format", "fmt", default="ascii",
              type=click.Choice(["dot", "mermaid", "ascii"]))
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def graph(recipe: Path, fmt: str, out: Path | None,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Render a recipe's DAG in the requested format."""
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

    steps = data.get("steps") or []
    g = nx.DiGraph()
    for s in steps:
        g.add_node(s["id"])
        for dep in s.get("needs") or []:
            g.add_edge(dep, s["id"])

    nodes = list(g.nodes())
    edges = list(g.edges())

    if fmt == "dot":
        text = _to_dot(edges, nodes, data.get("name", recipe.stem))
    elif fmt == "mermaid":
        text = _to_mermaid(edges, nodes)
    else:
        try:
            gens = [list(gen) for gen in nx.topological_generations(g)]
        except nx.NetworkXUnfeasible:
            die("pipeline has a cycle", code=EXIT_INPUT, as_json=as_json)
        text = _to_ascii(gens, edges)

    if as_json:
        emit_json({"format": fmt, "content": text, "nodes": nodes, "edges": edges})
        return

    if out is None or str(out) == "-":
        sys.stdout.write(text)
    else:
        safe_write(out, lambda f: f.write(text.encode("utf-8")),
                   force=force, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {out}", err=True)
