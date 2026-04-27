# `claw pipeline` — YAML Workflow Reference

Declarative DAG runner for multi-step `claw` tasks.

## Contents

- **EXECUTION**
  - [Run pipeline](#11-run) (use `--resume` to skip successful upstream steps)
- **INSPECTION**
  - [Validate recipe](#21-validate) · [Show graph](#22-graph) · [List steps](#23-list-steps)

---

## Critical Rules

1. **Interpolation** — Use `${step.output}` to link dependencies.
2. **Content Hashing** — Pipelines only re-run steps if inputs or logic change.
3. **Resumability** — Failed runs can be resumed with `--resume` to skip successful upstream steps.

---

## 1.1 run
Execute a YAML pipeline recipe as a DAG. Pass `--resume` to skip cache-hit steps whose inputs / logic are unchanged. Bound execution with `--from`/`--until` step names; tune parallelism with `--jobs`.
```bash
claw pipeline run <RECIPE.yaml> [--jobs N] [--resume] [--from <STEP>] [--until <STEP>] [--var KEY=VAL]... [--progress auto|json]
```

---

## 2.1 validate
Statically check a recipe for syntax errors and circular dependencies.
```bash
claw pipeline validate <RECIPE.yaml> [--json]
```

## 2.2 graph
Render the pipeline DAG as Mermaid, Graphviz DOT, or ASCII.
```bash
claw pipeline graph <RECIPE.yaml> [--format dot|mermaid|ascii] [--out <PATH>]
```

## 2.3 list-steps
Enumerate all available step types (shell, xlsx, pdf, etc.) and their schemas.
```bash
claw pipeline list-steps [--json]
```

---

## Footguns
- **Race Conditions** — Parallel steps writing to the same file will cause corruption. Ensure unique `--out` paths.
- **Environment** — `${env:VAR}` must be set in the shell before calling `pipeline run`.

## Escape Hatch
- [Nextflow](https://www.nextflow.io/) · [Snakemake](https://snakemake.github.io/) (for massive HPC pipelines).

---

## Quick Reference
| Task | Command |
|------|---------|
| Run Recipe | `claw pipeline run build.yaml` |
| Check Syntax | `claw pipeline validate recipe.yaml` |
| Resume Latest | `claw pipeline run recipe.yaml --resume` |
| List Step Types | `claw pipeline list-steps` |
