# `claw doctor` — Environment Diagnostics

`claw doctor` inspects everything `claw` depends on and prints one row per check. It mirrors `scripts/healthcheck.py` (the skill-level Python healthcheck) but runs from the shipped `claw` binary, so agents can invoke it anywhere `claw` is installed.

The rule: **`claw doctor` must pass clean before any `claw pipeline run` in CI**. Every failing row is either auto-fixable (`--fix`) or has a copy-paste install hint.

## Contents

- **RUN a diagnostic**
  - [`claw doctor`](#1-claw-doctor) · [`claw doctor --json`](#2-claw-doctor---json) · [`claw doctor --fix`](#3-claw-doctor---fix)
- **UNDERSTAND a check**
  - [Checks performed](#4-checks-performed) · [Output format](#5-output-format) · [Status icons](#6-status-icons)
- **INTEGRATE with CI**
  - [Exit codes](#7-exit-codes) · [Scoping checks](#8-scoping-checks)

---

## Critical Rules

1. **Doctor is read-only unless `--fix`.** Probes must not mutate config, install files, or touch caches.
2. **Every failure has a hint.** If `claw doctor` prints `[✗]` without an install / repair command, that's a bug.
3. **`--fix` is conservative.** Only Python pip extras and `uv tool sync` are auto-installed; external binaries print their `winget` / `apt` / `brew` command instead of executing it.
4. **Exit `0` on all-pass, `4` on any `[✗]`, `3` on any `[!]` (warning only).** CI branches on these.
5. **Run clean against a bare venv.** Doctor does not assume `./claw.toml` or any user config exists.

---

## 1. `claw doctor`

Human-readable table.

```
$ claw doctor
claw doctor
───────────
[✓] python 3.12.3
[✓] claw 1.4.0
[✓] openpyxl 3.1.5
[✓] python-docx 1.1.2
[✓] python-pptx 0.6.23
[✓] pymupdf 1.24.11          (fitz)
[✓] pypdf 4.3.1
[✓] pdfplumber 0.11.4
[✓] reportlab 4.2.2
[✓] Pillow 10.4.0
[✓] lxml 5.3.0
[✓] beautifulsoup4 4.12.3
[✓] ffmpeg 7.0                (H:\tools\ffmpeg\bin\ffmpeg.exe)
[✓] magick 7.1.1-38           (C:\Program Files\ImageMagick\magick.exe)
[✓] pandoc 3.4
[✓] qpdf 11.9.1
[✗] tesseract not installed   — install: winget install UB-Mannheim.TesseractOCR
[✓] exiftool 13.00
[✓] gws 0.14.2                — authenticated (scopes: gmail.send, drive.file, docs) — OK for email, doc build
[✓] clickup 0.8.1
[✓] node 22.8.0
[✓] npx 10.8.3
[!] pandoc PDF engine: xelatex found but 'unicode-math' tex package missing — install: tlmgr install unicode-math
[✓] ~/.config/claw/config.toml (valid)
[!] ./claw.toml has unknown keys: ['undocumented-field']
[✓] $XDG_CACHE_HOME/claw/ writable (2.3 GB, 1420 entries)

21 checks: 19 ok, 2 warnings, 1 failed
```

Ordering: language runtime → `claw` itself → Python packages → external CLIs → LaTeX (only if Pandoc present and PDF output ever requested) → auth (`gws`, Gmail API) → config files → cache directory.

## 2. `claw doctor --json`

Machine output, one NDJSON record per check, then a final summary.

```
$ claw doctor --json
{"check": "python", "status": "ok", "version": "3.12.3", "path": "/usr/bin/python3"}
{"check": "openpyxl", "status": "ok", "version": "3.1.5"}
{"check": "tesseract", "status": "fail", "hint": "winget install UB-Mannheim.TesseractOCR", "doc_url": "https://claw.dev/doctor/tesseract"}
{"check": "pandoc-latex-unicode-math", "status": "warn", "hint": "tlmgr install unicode-math"}
{"check": "claw-toml", "status": "warn", "path": "./claw.toml", "unknown_keys": ["undocumented-field"]}
{"summary": true, "total": 21, "ok": 19, "warn": 2, "fail": 1}
```

Each record always includes `check` and `status`; additional fields are check-specific. The trailing `{"summary": true, ...}` makes programmatic consumption trivial (`jq 'select(.summary)'`).

## 3. `claw doctor --fix`

Attempts repair where safe. Scope:

| Check | Auto-fix |
|-------|----------|
| Missing Python package in current venv | `uv pip install <pkg>` (falls back to `pip install`) |
| `uv tool` drift | `uv tool sync` |
| `./claw.toml` unknown keys | Prints the diff; **does not edit** — user reviews |
| Missing external binary (ffmpeg, pandoc, magick, etc.) | Prints install command; does not execute |
| Missing LaTeX package | Prints `tlmgr install ...`; does not execute |
| `gws` not authenticated | Prints `gws auth login`; does not execute |
| Cache dir not writable | Attempts `mkdir -p` + chmod; prints hint on failure |

Rationale: package-manager calls (`winget install`, `apt`, `brew`) require privilege or prompts and are dangerous to run headless. Doctor tells you the right command; you run it.

## 4. Checks performed

### 4.1 Python runtime & packages

- `python --version` — must be ≥ 3.11 (fails otherwise; `claw` uses `typing.Self`, `tomllib`, PEP-695 generics).
- Installed package versions for: `openpyxl`, `python-docx`, `python-pptx`, `pymupdf` (import `fitz`), `pypdf`, `pdfplumber`, `reportlab`, `Pillow` (import `PIL`), `lxml`, `beautifulsoup4` (import `bs4`).
- Each package also checks for known-broken version ranges (e.g. `Pillow < 10.0` on Python 3.12).

### 4.2 External CLIs

Resolved via `shutil.which`, versions parsed from `--version`:

| Tool | Used by | Install hint |
|------|---------|--------------|
| `ffmpeg` | `claw media` | `winget install Gyan.FFmpeg` |
| `magick` | `claw img` | `winget install ImageMagick.ImageMagick` |
| `pandoc` | `claw convert` | `winget install JohnMacFarlane.Pandoc` |
| `qpdf` | `claw pdf` (linearization) | `winget install QPDF.QPDF` |
| `tesseract` | `claw pdf ocr`, `claw img ocr` | `winget install UB-Mannheim.TesseractOCR` |
| `exiftool` | `claw img meta`, `claw media meta` | `winget install OliverBetz.ExifTool` |
| `gws` | `claw email`, `claw doc`, `claw sheet` | `npm install -g @anthropic/gws` |
| `clickup` | `claw clickup` (if plugin enabled) | See [setup.md § 2](../setup.md#2-cli-tools) |
| `node` | `gws`, LSP plugins | `winget install OpenJS.NodeJS` |
| `npx` | MCP servers | (ships with node) |

### 4.3 LaTeX packages (conditional)

Only runs if `pandoc` is present. Checks packages commonly required by Pandoc's PDF engines:

| Package | Needed for |
|---------|------------|
| `amsfonts` | Math symbols in default template |
| `unicode-math` | `xelatex` / `lualatex` math rendering |
| `booktabs` | Pandoc's default table style |
| `geometry` | `-V geometry:margin=1in` flag |

Probe strategy:

1. Parse `tlmgr list --only-installed` (TeX Live).
2. Fallback: `kpsewhich <pkg>.sty` returns a path.
3. If both fail and the distribution is MiKTeX, use `mpm --list` via `shutil.which("mpm")`.

### 4.4 Google Workspace auth

Runs `gws auth status` (Windows-shim-safe — resolved via `shutil.which`).

- Reports authenticated account + granted scopes.
- Flags scope insufficiency per claw feature:
  - `claw email send` requires `gmail.send`
  - `claw doc build` / `doc create` requires `docs` + `drive.file`
  - `claw sheet upload` requires `drive.file` + `spreadsheets`
- A missing scope is `[!]` (warning) with the hint `gws auth login --scope ...`.

### 4.5 Gmail API enabled in Cloud Console

Indirect probe: runs `gws gmail users getProfile --params '{"userId":"me"}'` with a low timeout.

- `403 PERMISSION_DENIED` with message containing `gmail.googleapis.com` → Gmail API not enabled on the account's Cloud project. Hint: URL to the Console `Enable API` page.
- Network / timeout → `[!]` with hint to re-run doctor online.

### 4.6 Config files

- Existence check for `./claw.toml` (optional) and `~/.config/claw/config.toml` (optional).
- Parse with `tomllib`; syntax errors → `[✗]`.
- Schema check against the published `claw.config.schema.json`:
  - Unknown top-level keys → `[!]` with the list.
  - Known key with wrong type → `[✗]`.
- `claw config show --json` is the authoritative resolved view; doctor links to it in the hint.

### 4.7 Cache directory

- `$XDG_CACHE_HOME/claw/` (or `%LOCALAPPDATA%\claw\cache\`) exists and is writable.
- Reports total size and entry count.
- Warns `[!]` if size > 10 GB (hint: `claw cache clear --older-than 30d`).

## 5. Output format

Three modes:

| Mode | Flag | Stream |
|------|------|--------|
| Human table | default | stdout |
| NDJSON | `--json` | stdout |
| Prometheus metrics | `--prometheus` | stdout |

Prometheus form (for long-running agents / monitoring):

```
# HELP claw_doctor_check Status of a claw doctor check (1=ok, 0.5=warn, 0=fail)
# TYPE claw_doctor_check gauge
claw_doctor_check{check="python"} 1
claw_doctor_check{check="tesseract"} 0
claw_doctor_check{check="pandoc_latex_unicode_math"} 0.5
```

## 6. Status icons

| Icon | JSON `status` | Exit contribution | Meaning |
|------|---------------|-------------------|---------|
| `[✓]` | `ok` | nothing | Passes; ready to use |
| `[!]` | `warn` | bumps exit to at least `3` | Works but with caveats (missing optional dep, unknown config key, soft scope gap) |
| `[✗]` | `fail` | bumps exit to `4` | Hard failure; affected `claw` features will not run |

Under `--color=never` the icons fall back to `OK / WARN / FAIL`.

## 7. Exit codes

| Exit | Condition |
|------|-----------|
| `0` | Every check `[✓]` |
| `3` | At least one `[!]`, no `[✗]` |
| `4` | At least one `[✗]` |
| `2` | Usage error (bad flag) |
| `5` | Doctor itself crashed (bug — report via `--doc_url`) |

## 8. Scoping checks

By default doctor runs everything. For faster CI, narrow the scope:

```
claw doctor --scope python          # only Python package checks
claw doctor --scope cli             # only external CLIs
claw doctor --scope auth            # only gws / Gmail API
claw doctor --scope config          # only ./claw.toml + ~/.config/claw/
claw doctor --scope cache           # only cache directory
claw doctor --scope pipeline        # deps needed for claw pipeline run
claw doctor --scope email           # deps needed for claw email send
```

Multiple scopes compose: `--scope python --scope auth`.

`--scope pipeline` dynamically computes deps from a recipe: `claw doctor --scope pipeline --recipe recipe.yaml` checks exactly the step types referenced.

---

## Quick Reference

| Task | Command |
|------|---------|
| Full check | `claw doctor` |
| Machine output | `claw doctor --json` |
| Auto-install Python deps | `claw doctor --fix` |
| Only auth | `claw doctor --scope auth` |
| Per-recipe | `claw doctor --scope pipeline --recipe recipe.yaml` |
| Prometheus metrics | `claw doctor --prometheus` |
| CI gate | `claw doctor --json \| jq -e 'select(.summary) \| .fail == 0'` |
