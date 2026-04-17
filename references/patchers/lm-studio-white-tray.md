# LM Studio — White Tray Icon Patcher

On-demand patcher that replaces LM Studio's colored tray icon with a white-bars silhouette. Re-run `apply` after any LM Studio update (the updater overwrites `icon.ico`).

## Contents

- **WHITEN LM Studio tray icon** — swap colored icon for a white-bars silhouette
  - [How it works (what LM Studio reads on Windows)](#how-it-works)
  - [Usage (apply / restore / status)](#usage)
- **CUSTOMIZE the icon design**
  - [Edit `BARS_64` + regenerate](#customize-icon-design)
- **TROUBLESHOOT**
  - [Critical rules (Windows-only, UAC, update behavior)](#critical-rules)
  - [Symptom → fix table](#troubleshooting)
  - [Quick-reference commands](#quick-reference)

---

## Critical Rules

1. **Windows-only.** Hardcoded path `C:\Program Files\LM Studio\resources\icon.ico`; no macOS/Linux support.
2. **Admin required for apply/restore.** Script self-elevates via UAC. `status` doesn't need it.
3. **Original backed up once.** `icon.ico` -> `icon.original.ico` on first apply. Never overwritten. `restore` copies the backup back over `icon.ico`.
4. **Icon design lives in `BARS_64` inside the script itself.** Edit the constant, then re-run `apply` — the white `.ico` is rendered in-memory from `BARS_64` on every invocation.
5. **No background watcher.** LM Studio updates revert the icon; manually re-run `apply` afterwards.

---

## How It Works

LM Studio's obfuscated main bundle (`resources/app/.webpack/main/index.js`) defines `trayIconPath()`. On `win32`, it returns a single hardcoded path — `path.join(process.resourcesPath, 'icon.ico')` — ignoring tray state (active / paused) and system theme. On macOS/Linux it uses the `trayIcon{,Active,Paused}{,Dark}Template.png` variants, but Windows never touches those PNGs. Only `icon.ico` matters.

The patcher:
1. Renders a multi-size `.ico` (16/20/24/32/40/48/64/128/256 px) of white horizontal bars on transparent background, in-memory from the `BARS_64` constant.
2. Hash-checks the installed `icon.ico` against the freshly-rendered white version.
3. On drift, backs up the original once, writes the white `.ico` over it.

---

## Usage

```bash
# First-time or after an LM Studio update:
python ~/.claude/skills/claude-claw/scripts/patchers/lm-studio-white-tray.py apply

# Revert to LM Studio's original:
python ~/.claude/skills/claude-claw/scripts/patchers/lm-studio-white-tray.py restore

# Check current state (hashes, backup presence):
python ~/.claude/skills/claude-claw/scripts/patchers/lm-studio-white-tray.py status
```

After `apply`, fully quit LM Studio from the tray (right-click -> Quit — not just close the window) and relaunch to see the new icon.

---

## Customize Icon Design

Edit `BARS_64` near the top of `scripts/patchers/lm-studio-white-tray.py`. Each tuple is `(y_center, x_start, x_end, thickness)` in a 64x64 coordinate grid. Bars have rounded caps automatically.

```python
BARS_64 = [
    (15, 14, 40, 4),   # left-aligned row 1
    (23, 30, 50, 4),   # right-aligned row 2
    (31, 14, 50, 5),   # left-aligned row 3 (longest)
    (40, 24, 50, 4),   # right-aligned row 4
    (48, 14, 38, 4),   # left-aligned row 5
]
```

Then re-push to LM Studio:

```bash
python ~/.claude/skills/claude-claw/scripts/patchers/lm-studio-white-tray.py apply
```

`apply` re-renders from the current `BARS_64` every run, so there's no separate `regenerate` step.

---

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Icon still colored after apply | Fully quit LM Studio from the tray (right-click -> Quit). Closing the window keeps it running. |
| "LM Studio not installed" | `C:\Program Files\LM Studio\resources\icon.ico` missing. Install LM Studio, or adjust `LM_STUDIO_RESOURCES` if installed elsewhere. |
| UAC declined | Re-run; script exits cleanly when elevation is refused. |
| Update reverted the icon | Expected — just re-run `apply`. |

---

## Quick Reference

| Task | Command |
|------|---------|
| Apply white icon | `python lm-studio-white-tray.py apply` |
| Revert to original | `python lm-studio-white-tray.py restore` |
| Check state | `python lm-studio-white-tray.py status` |
| Change bar layout | edit `BARS_64` in the script → `apply` |
