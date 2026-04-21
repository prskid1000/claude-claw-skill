# `claw doctor` — Diagnostics Reference

CLI tool for environment verification and dependency health checks.

## Contents

- **DIAGNOSTICS**
  - [Run all checks](#11-run) · [Verify system](#12-system) · [Verify MCP](#13-mcp)

---

## Critical Rules

1. **Venv Scope** — Doctor checks the Python environment it is currently running in.
2. **Path Verification** — Ensures external binaries (ffmpeg, pandoc, magick) are correctly indexed.
3. **JSON Output** — Use `--json` for automated health-monitoring integration.

---

## 1.1 run
Execute the full suite of diagnostic tests.
```bash
claw doctor [--json] [--fix]
```

## 1.2 system
Verify system-level dependencies (OS, Disk, TTY).
```bash
claw doctor system [--json]
```

## 1.3 mcp
Check health and configuration of integrated MCP servers (MySQL, Browser).
```bash
claw doctor mcp [--json]
```

---

## Quick Reference
| Task | Command |
|------|---------|
| Full Check | `claw doctor` |
| JSON Report | `claw doctor --json` |
| Auto-fix Issues | `claw doctor --fix` |
