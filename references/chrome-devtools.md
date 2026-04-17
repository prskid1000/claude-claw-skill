# Chrome DevTools MCP — Browser Launch Reference

> **TL;DR: use `claw browser launch` for the launch step.** See [references/claw/browser.md](claw/browser.md) — it handles the `--user-data-dir` footgun, kill-before-relaunch dance, and readiness polling. This reference keeps the manual binary invocation for cases where `claw browser` can't be used (custom flags, alternate browsers) plus the Chrome DevTools MCP post-launch tool-call model.

## Contents

- **AUTOMATE browser** — Chrome DevTools MCP
  - [Critical rules (debug port, `--user-data-dir` gotcha)](#critical-rules)
  - [Launch via `claw browser` (preferred)](#launch-via-claw-browser)
  - [Manual invocation (escape hatch)](#manual-invocation-escape-hatch)
  - [Verification (`/json/version` check)](#verification)
  - [Quick reference](#quick-reference)

> Examples: [examples/chrome-devtools.md](../examples/chrome-devtools.md) · install via [setup.md](setup.md#4-mcp-servers)

---

## Critical Rules

1. **The browser MUST be launched with `--remote-debugging-port=9222`.** You cannot enable the debug port on an already-running browser.
2. **Always pass `--user-data-dir`.** Without it, if any other browser process is already running, the new launch silently attaches to the existing instance and the flag is ignored — port 9222 never opens. This is the single most common failure mode. `claw browser launch` always passes it.
3. **Default profile requires killing all existing browser processes first** — the data dir is locked while any process holds it. Background tabs and the system-tray helper count. `claw browser launch --profile default --force` does this safely.
4. **Verify before retrying MCP calls.** If `list_pages` returns a connection error, the port isn't open. Fix the launch — don't re-call the MCP tool.

---

## Launch via `claw browser`

Preferred path — handles kill-before-relaunch, resolves the correct `--user-data-dir`, polls `/json/version` for readiness, emits JSON with PID / WebSocket URL.

| Task | `claw` command |
|---|---|
| Edge, default profile (preserves cookies / logins) | `claw browser launch --force` |
| Edge, throwaway profile | `claw browser launch --profile throwaway` |
| Chrome, default profile | `claw browser launch --browser chrome --force` |
| Chrome, throwaway profile | `claw browser launch --browser chrome --profile throwaway` |
| Custom port | `claw browser launch --profile throwaway --port 9333` |
| JSON for MCP attach | `claw browser launch --force --json` |
| Stop + clean up throwaway dir | `claw browser stop --port 9222 --cleanup` |

See [claw/browser.md](claw/browser.md) for full flag surface.

---

## Manual invocation (escape hatch)

Drop to the raw binary only when `claw browser` doesn't fit — custom Chromium flags (`--disable-gpu`, `--window-size=...`, proxy), Firefox remote-debugging, or headless mode.

### Edge — default profile (preserves cookies/logins)

```bash
taskkill //F //IM msedge.exe         # kill all Edge processes first
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:/Users/$USER/AppData/Local/Microsoft/Edge/User Data" &
```

### Edge — isolated profile (no kill needed)

```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:/temp/edge-debug" &
```

### Chrome

Same flags, different binary path:

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:/temp/chrome-debug" &
```

Default profile path: `C:\Users\<user>\AppData\Local\Google\Chrome\User Data`.

**PowerShell quoting**: a quoted path is a string, not a command — prefix with `&` to invoke. From bash / Git Bash / MSYS2, plain quoted path works. `claw browser` bypasses this because it spawns via `subprocess`, no shell.

---

## Verification

```bash
curl -s http://127.0.0.1:9222/json/version
```

Success returns JSON with `Browser`, `webSocketDebuggerUrl`. Exit code 7 = port not open (browser didn't launch with the flag, or attached to existing instance — see Critical Rule #2).

`claw browser verify --port 9222` does this with exit code 6 on timeout.

---

## Quick Reference

| Task | Command |
|------|---------|
| Launch (preferred) | `claw browser launch --force` |
| Launch throwaway | `claw browser launch --profile throwaway` |
| Kill all Edge (manual) | `taskkill //F //IM msedge.exe` |
| Kill all Chrome (manual) | `taskkill //F //IM chrome.exe` |
| Verify port (manual) | `curl -s http://127.0.0.1:9222/json/version` |
| Verify port (`claw`) | `claw browser verify --port 9222` |
| Stop + cleanup | `claw browser stop --port 9222 --cleanup` |
| MCP plugin args | `["chrome-devtools-mcp@latest", "--browserUrl=http://127.0.0.1:9222"]` |
