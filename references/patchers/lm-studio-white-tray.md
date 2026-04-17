# LM Studio — White Tray Icon Patcher

On-demand patcher that replaces LM Studio's colored tray icon with a white-bars silhouette. Re-run `apply` after any LM Studio update (the updater overwrites `icon.ico`).

## Contents

- [Critical Rules](#critical-rules)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Customize Icon Design](#customize-icon-design)
- [Troubleshooting](#troubleshooting)

---

## Critical Rules

1. **Windows-only.** Hardcoded path `C:\Program Files\LM Studio\resources\icon.ico`; no macOS/Linux support.
2. **Admin required for apply/restore.** Script self-elevates via UAC. Status and regenerate don't need it.
3. **Original backed up once.** `icon.ico` -> `icon.original.ico` on first apply. Never overwritten. `restore` copies the backup back over `icon.ico`.
4. **Icon design lives in `make-white-ico.py`.** Edit the `BARS_64` constant, run `regenerate`, then `apply`.
5. **No background watcher.** LM Studio updates revert the icon; manually re-run `apply` afterwards.

---

## How It Works

LM Studio's obfuscated main bundle (`resources/app/.webpack/main/index.js`) defines `trayIconPath()`. On `win32`, it returns a single hardcoded path — `path.join(process.resourcesPath, 'icon.ico')` — ignoring tray state (active / paused) and system theme. On macOS/Linux it uses the `trayIcon{,Active,Paused}{,Dark}Template.png` variants, but Windows never touches those PNGs. Only `icon.ico` matters.

The patcher:
1. Renders a multi-size `.ico` (16/20/24/32/40/48/64/128/256 px) of white horizontal bars on transparent background via `make-white-ico.py`.
2. Hash-checks the installed `icon.ico` against the white version.
3. On drift, backs up the original once, copies the white `.ico` over it.

---

## Usage

```bash
# First-time or after an LM Studio update:
python ~/.claude/skills/claude-claw/scripts/lm-studio-white-tray/lm-studio-white-tray.py apply

# Revert to LM Studio's original:
python ~/.claude/skills/claude-claw/scripts/lm-studio-white-tray/lm-studio-white-tray.py restore

# Check current state (hashes, backup presence):
python ~/.claude/skills/claude-claw/scripts/lm-studio-white-tray/lm-studio-white-tray.py status
```

After `apply`, fully quit LM Studio from the tray (right-click -> Quit — not just close the window) and relaunch to see the new icon.

---

## Customize Icon Design

Edit `BARS_64` at the top of `scripts/lm-studio-white-tray/make-white-ico.py`. Each tuple is `(y_center, x_start, x_end, thickness)` in a 64x64 coordinate grid. Bars have rounded caps automatically.

```python
BARS_64 = [
    (15, 14, 40, 4),   # left-aligned row 1
    (23, 30, 50, 4),   # right-aligned row 2
    (31, 14, 50, 5),   # left-aligned row 3 (longest)
    (40, 24, 50, 4),   # right-aligned row 4
    (48, 14, 38, 4),   # left-aligned row 5
]
```

Then:

```bash
python lm-studio-white-tray.py regenerate   # re-renders white-icon.ico
python lm-studio-white-tray.py apply        # pushes to LM Studio (UAC)
```

You can also replace `white-icon.ico` directly with any valid multi-size `.ico` (transparent background recommended); `apply` uses whatever that file contains.

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
| Change bar layout | edit `BARS_64` -> `regenerate` -> `apply` |
