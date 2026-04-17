# Claude Apps — Customization Toolkit

Umbrella overview of the two modification approaches + four launch wrappers for
running the official Claude products (Code, Desktop) against a local-model
backend (LM Studio → telecode proxy) and lifting hard-coded limits.

## Contents

- **COMPARE the approaches** — which tool hits which surface
  - [At a glance (comparison table)](#at-a-glance)
  - [Why two different approaches](#why-two-different-approaches)
- **LAUNCH with local-model env**
  - [Launch wrappers (codel / claudel / claudedl / codexl)](#launch-wrappers)
  - [Installing the wrappers to PATH](#installing-the-wrappers)
- **DECIDE what to use**
  - [When to use what](#when-to-use-what)
- **PATCH Claude Code binary** — see [claude-patcher.md](patchers/claude-patcher.md)
- **TOGGLE Claude Desktop 3P (BYOM)** — see [claude-desktop-3p.md](patchers/claude-desktop-3p.md)

---

## At a Glance

| Tool | Target | What it changes | Reversible? | Survives updates? |
|---|---|---|---|---|
| [`claude-patcher.js`](patchers/claude-patcher.md) | Claude Code binary | Patches numeric constants in `claude.exe` (context window, output cap, autocompact, summary size) | Yes (`--restore` from `.bak`) | Re-run after each update |
| [`claude-desktop-3p.py`](patchers/claude-desktop-3p.md) | Claude Desktop | Writes Anthropic's enterprise registry policy (HKCU + HKLM\\SOFTWARE\\Policies\\Claude) | Yes (`disable` deletes keys) | Yes — registry is decoupled from binary |
| `wrappers/*.bat` | Per-process launch | Sets env vars before exec'ing tool — points it at telecode proxy | n/a (no persistent state) | Yes |

## Why Two Different Approaches

**Claude Code** is a Node.js CLI compiled into a single executable. It already
respects `ANTHROPIC_BASE_URL`, so pointing inference at telecode is just an env
var (see wrappers below). The **patcher** exists for a separate problem:
unlocking hard-coded window/output limits the CLI doesn't expose as flags.
Numeric constants live inside the bundled JS — patched by value with structural
anchors so it survives variable-name changes from minification.
See [claude-patcher.md](patchers/claude-patcher.md) for the detail.

**Claude Desktop** is an Electron wrapper around `claude.ai`. It does NOT
respect `ANTHROPIC_BASE_URL` for its main chat window — that flow runs through
the claude.ai backend, gated by your subscription tier. But Anthropic shipped a
first-party **Custom 3P** (BYOM) deployment mode for enterprise customers: set
specific registry values and the app:
- skips claude.ai login,
- serves a synthetic Pro org with `capabilities: ["chat", "claude_pro"]`,
- routes inference to your gateway URL,
- unlocks Cowork + Claude Code surfaces in the UI.

The script just writes those registry values. **No binary patching needed** —
the field names (`inferenceProvider`, `inferenceGatewayBaseUrl`, etc.) are
Anthropic's stable enterprise-config schema and don't change across updates.
See [claude-desktop-3p.md](patchers/claude-desktop-3p.md) for the detail.

---

## Launch Wrappers

Living at `~/.claude/skills/claude-claw/scripts/wrappers/`. These are `.bat`
files; copy them to any directory on `PATH` (e.g. `%USERPROFILE%\Scripts`) and
they become globally callable commands.

| Wrapper | Launches | What it sets |
|---|---|---|
| `codel.bat` | `code-insiders` | Local-model env so Claude Code VS Code extension uses telecode |
| `claudel.bat` | `claude` (CLI) | Same env, plus `--dangerously-skip-permissions` |
| `claudedl.bat` | Claude Desktop (MSIX) | Same env (inherited by bundled CC subprocess) + dynamic MSIX path resolution via `Get-AppxPackage` |
| `codexl.bat` | `codex` (OpenAI Codex CLI) | `--oss -m qwen3.5-35b-a3b` |

Common env block (`claudel`, `codel`, `claudedl`):
- `ANTHROPIC_BASE_URL=http://localhost:1235` — telecode proxy
- `ANTHROPIC_AUTH_TOKEN=lmstudio` — any string, telecode ignores
- `ANTHROPIC_MODEL=qwen3.5-35b-a3b` — model ID telecode forwards to LM Studio
- `DISABLE_PROMPT_CACHING=1` — cache_control breaks LM Studio
- `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` — Windows shell preference
- `BASH_*_TIMEOUT_MS` — long-running command tolerance
- `CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192` — cap output for slower local models
- `ENABLE_TOOL_SEARCH=false` — don't use Anthropic's ToolSearch (telecode injects its own)

`claudedl.bat` extras:
- `DEFAULT_LLM_MODEL` — Operon/Cowork default
- Dynamic resolution: `for /f ... powershell ... Get-AppxPackage -Name 'Claude'` finds the MSIX install path so the wrapper survives Claude Desktop version bumps
- Optional debug envs commented out (uncomment to capture `[custom-3p]` / `[oauth]` traces in `main.log`)

---

## Installing the Wrappers

```powershell
# Pick a directory on PATH
$dest = "$env:USERPROFILE\Scripts"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

# Copy all four
Copy-Item ~/.claude/skills/claude-claw/scripts/wrappers/*.bat $dest

# Verify $dest is on PATH
$env:PATH -split ';' | Select-String -Pattern ([regex]::Escape($dest))
```

Or one-shot copy a single one:

```bash
cp ~/.claude/skills/claude-claw/scripts/wrappers/claudedl.bat ~/Scripts/
```

### Combining Both for Claude Desktop

To get Claude Desktop fully on local inference (chat UI + bundled subprocesses):

```bash
# 1) One-time: enable 3P mode (registry policy → unlocks chat UI + Cowork/Code tabs)
python ~/.claude/skills/claude-claw/scripts/patchers/claude-desktop-3p.py enable

# 2) Each launch: env wrapper (so bundled Claude Code / Cowork agents see local model)
claudedl
```

`(1)` is registry — persists across reboots. `(2)` is per-process env — sets
inheritance for any subprocess Claude Desktop spawns.

---

## When To Use What

- **Just want Claude Code CLI on local model?** Use `claudel.bat`. No patching.
- **Want bigger context / output in Claude Code?** Add `claude-patcher.js --all`.
  See [claude-patcher.md](patchers/claude-patcher.md).
- **Want Claude Desktop on local model + Cowork/Code tabs?** Run
  `claude-desktop-3p.py enable` and launch via `claudedl.bat`.
  See [claude-desktop-3p.md](patchers/claude-desktop-3p.md).
- **Just the VS Code extension on local model?** Use `codel.bat`.
- **Whiten LM Studio's tray icon?** See [lm-studio-white-tray.md](patchers/lm-studio-white-tray.md).
- **Roll back any of it?** `--restore` for the patcher, `disable` for the
  desktop toggle, or just don't use the wrapper.
