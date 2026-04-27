# `claw doctor` — Diagnostics Reference

Flat command that checks external dependencies and auth in one pass. No subcommands.

## Contents

- **DIAGNOSTICS**
  - [Run checks](#11-doctor)

---

## Critical Rules

1. **Flat command** — `claw doctor` is a single command; there are no `doctor system` / `doctor mcp` subcommands.
2. **Exit codes** — `0` = all OK, `3` = warnings only, `4` = at least one failure. Useful for CI gating.
3. **Scopes** — `--scope` narrows what's checked: `all` (default), `packages` (Python deps in the claw venv), `cli` (external binaries like ffmpeg/pandoc/magick), `gws` (Google Workspace auth).
4. **No `--fix`** — Doctor only reports; it does not auto-repair. To repair the venv, run `python ~/.claude/skills/claude-claw/scripts/healthcheck.py --install` (or `--recreate-venv`).

---

## 1.1 doctor
Run dependency and auth checks. Emits a human-readable report by default; pass `--json` for machine-readable output.
```bash
claw doctor [--scope all|packages|cli|gws] [--json]
```

---

## Footguns
- **Exit 3 ≠ failure** — Warnings exit `3`, not `0`. CI scripts that treat any non-zero as failure will trip on warnings; gate on `< 4` if warnings are acceptable.
- **`--scope cli` ≠ shim resolution** — Doctor checks whether external binaries are reachable, but Python `subprocess.run([...])` calls still need `shutil.which()` to resolve `.cmd`/`.bat` shims on Windows.
- **No auto-fix** — There is no `--fix` flag. Doctor reports problems; you fix them manually (or via `healthcheck.py`).

## Escape Hatch
- Repair venv / Python deps: `python ~/.claude/skills/claude-claw/scripts/healthcheck.py --install`
- Wipe and rebuild venv: `python ~/.claude/skills/claude-claw/scripts/healthcheck.py --recreate-venv`
- Re-auth Google Workspace: `gws auth login`

---

## Quick Reference
| Task | Command |
|------|---------|
| Full Check | `claw doctor` |
| JSON Report | `claw doctor --json` |
| Python Deps Only | `claw doctor --scope packages` |
| External Binaries | `claw doctor --scope cli` |
| Google Auth | `claw doctor --scope gws` |
