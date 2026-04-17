# `claw browser` — Chromium Launcher for MCP Debug-Protocol Reference

Single-purpose CLI for launching Edge or Chrome with the remote-debugging port open, so the Chrome DevTools MCP can attach. Handles the `--user-data-dir` footgun, the kill-before-relaunch dance, and emits the WebSocket URL on success.

Library / MCP-side reference: [references/chrome-devtools.md](../chrome-devtools.md).

## Contents

- **LAUNCH Chromium with debug port**
  - [Default profile (preserves cookies/logins)](#11-launch-default) · [Throwaway profile (fast, isolated)](#12-launch-throwaway)
- **VERIFY the port is open**
  - [Poll `/json/version` until ready](#21-verify)
- **STOP the debug instance**
  - [Taskkill the launched process](#31-stop)
- **When `claw browser` isn't enough** — [escape hatches](#when-claw-isnt-enough)

---

## Critical Rules

1. **Safe-by-default launches** — `claw browser launch --profile default` detects existing `msedge.exe` / `chrome.exe` processes and **refuses to kill them** without `--force`. The data dir is locked while any process holds it; silently killing the user's open browser would be a productivity disaster.
2. **`--user-data-dir` is always passed** — never omit it. Without `--user-data-dir`, if any other browser process is already running, the new launch silently attaches to the existing instance, the debug-port flag is ignored, and port 9222 never opens. This is the single most common failure. `claw` always passes it; `launch --profile default` resolves it to the real profile path, `--profile throwaway` creates a fresh temp dir.
3. **Structured output** — `launch` emits a single JSON object `{pid, port, websocket_url, profile, user_data_dir, browser}` with `--json`. On failure: `{error, code, hint, doc_url}` to stderr.
4. **Exit codes** — `0` success, `1` generic, `2` usage error, `4` precondition failed (existing browser process, no `--force`), `5` system error (binary not found), `6` port didn't open within timeout, `130` SIGINT.
5. **Help** — `claw browser --help`, `claw browser <verb> --help`, `--examples` prints runnable recipes.
6. **Readiness polling** — `launch` doesn't return until `http://127.0.0.1:<port>/json/version` returns 200 (or timeout). Default 15 s; override with `--timeout SEC`.
7. **Platform** — Windows only (matches the rest of claude-claw's scope). The binary-discovery logic looks at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` and `C:\Program Files\Google\Chrome\Application\chrome.exe` by default. Override with `--binary PATH`.

---

## 1. LAUNCH

### 1.1 `launch --profile default`

Launch with the user's real profile — preserves cookies, logged-in sessions, extensions. Requires killing any existing browser processes first (the profile directory is locked while any tab is open, including background tabs and the system-tray helper).

```
claw browser launch [--profile default] [--browser edge|chrome]
                    [--port 9222] [--user-data-dir PATH]
                    [--force] [--timeout 15] [--json]
```

Flags:

- `--profile default` (default when `--profile` omitted) — use the real user profile at `%LOCALAPPDATA%\Microsoft\Edge\User Data` (Edge) or `%LOCALAPPDATA%\Google\Chrome\User Data` (Chrome).
- `--browser edge` (default) or `--browser chrome`.
- `--port 9222` — debug port (default 9222, matching MCP convention).
- `--user-data-dir PATH` — override the resolved default path.
- `--force` — kill existing `msedge.exe` (or `chrome.exe`) processes before launching. Without this, exit 4 with a hint if any browser process is detected.
- `--timeout SEC` — max wait for `/json/version` to respond (default 15).

Examples:

```
claw browser launch --force
```

```
claw browser launch --browser chrome --force --json
```

Output (with `--json`):

```json
{
  "pid": 12840,
  "port": 9222,
  "websocket_url": "ws://127.0.0.1:9222/devtools/browser/...",
  "profile": "default",
  "user_data_dir": "C:/Users/prith/AppData/Local/Microsoft/Edge/User Data",
  "browser": "edge"
}
```

### 1.2 `launch --profile throwaway`

Launch with an isolated, temporary profile. No need to kill existing browser processes. Ideal for automated tests, headless-like scraping with JS rendering, or any scenario where logged-in state isn't needed.

```
claw browser launch --profile throwaway [--browser edge|chrome]
                                         [--port 9222] [--json]
```

Behavior:

- Creates a fresh directory via `mkdtemp()` under the system temp dir (e.g. `C:/Users/prith/AppData/Local/Temp/claw-browser-XXXXXX`).
- Launches without touching the user's real profile.
- Doesn't interfere with running browsers (as long as `--port` doesn't collide).
- Temp dir is NOT auto-cleaned on exit — `claw browser stop --cleanup` handles that. This matches Chrome's lifecycle (profile dir must persist until the process fully exits).

Examples:

```
claw browser launch --profile throwaway --json
```

```
claw browser launch --profile throwaway --port 9333 --browser chrome
```

---

## 2. VERIFY

### 2.1 `verify`

Poll `/json/version` until the debug port responds. Used internally by `launch`; exposed for scripting.

```
claw browser verify [--port 9222] [--timeout 15] [--json]
```

Output on success (`--json`):

```json
{
  "browser": "Microsoft Edge/122.0.2365.92",
  "protocol_version": "1.3",
  "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/browser/..."
}
```

Exit 6 if the port doesn't respond within the timeout.

Example:

```
claw browser verify --port 9222 || echo "port not open — check the launch"
```

---

## 3. STOP

### 3.1 `stop`

Gracefully terminate a browser launched by `claw`. Uses `taskkill /PID <pid> /T` (graceful) → 3 s grace → `taskkill /PID <pid> /T /F` (forceful) — the same pattern used in the VoxType services manager.

```
claw browser stop (--pid N | --port 9222) [--cleanup] [--force]
```

Flags:

- `--pid` — the PID emitted by `launch --json`.
- `--port` — discover the PID via the debug port's `/json/version` endpoint.
- `--cleanup` — remove the throwaway `--user-data-dir` after the process exits. Ignored for default-profile launches.
- `--force` — skip the graceful TERM, go straight to `/F`.

Example:

```
claw browser stop --port 9222 --cleanup
```

---

## When `claw browser` Isn't Enough

Drop into the Chrome DevTools MCP or the raw binary for:

| Use case | Why `claw browser` can't do it | Escape hatch |
|---|---|---|
| All browser automation after launch (click, navigate, screenshot, DOM snapshot, network list) | `claw browser` only handles the launch lifecycle | [Chrome DevTools MCP tools](../chrome-devtools.md) — `list_pages`, `new_page`, `navigate_page`, etc. |
| Launch with custom CLI flags (`--disable-gpu`, `--window-size=...`, proxy) | Not wrapped; intentionally minimal | `--extra-flag` is NOT supported — use the binary directly, or file an issue |
| Firefox remote-debugging | Not Chromium-family | Launch Firefox manually with `-remote-debugging-port` |
| Headless mode | Not wrapped (MCP prefers headful for anti-bot + visual verification) | Pass `--headless=new` via the raw binary; MCP may have attach issues |
| Persistent session across reboots | `stop` terminates the process | Use a scheduled task; see VoxType services model |
| Multiple simultaneous profiles | `claw browser` doesn't track launched instances | Launch with different `--port` values; track PIDs externally |

## Footguns

- **Port 9222 already bound** — could be another Chromium, or a leftover zombie from a previous session. `claw browser launch` fails fast with `code=PORT_IN_USE`. Use `claw browser stop --port 9222 --force` to clear.
- **`--user-data-dir` on a running browser** — silently ignored. Always kill first (`--force`) or use `--profile throwaway`.
- **Background tabs / system tray helper hold the profile lock** — closing the visible window isn't enough. Check Task Manager for `msedge.exe` / `chrome.exe` entries before assuming it's clean.
- **PowerShell quoting** — from PowerShell, prefix the binary path with `&`: `& "C:\Program Files ...\msedge.exe" ...`. From bash (Git Bash, MSYS2), plain quoted path works. `claw browser` bypasses all of this — it spawns with `subprocess`, no shell — but if you fall back to raw invocation, remember this.
- **`/json/version` returns instantly after launch** — no, it doesn't. The browser takes 500 ms – 3 s to bind the port on a cold start. Use `claw browser verify` or `launch --timeout`.
- **Throwaway profile temp-dir growth** — each throwaway launch creates a new ~50 MB directory. Always pair with `stop --cleanup` or run `claw browser cleanup` (future verb) to GC orphaned dirs.
- **`--force` kills BOTH Edge and Chrome if `--browser` chose the wrong one** — it only kills the process matching `--browser`. A running Edge will not be killed by `--force --browser chrome`, but the Chrome launch may still collide on port 9222. Pick a non-colliding port.

---

## Quick Reference

| Task | One-liner |
|------|-----------|
| Launch Edge default profile | `claw browser launch --force` |
| Launch Chrome default profile | `claw browser launch --browser chrome --force` |
| Launch throwaway | `claw browser launch --profile throwaway` |
| Launch on custom port | `claw browser launch --profile throwaway --port 9333` |
| JSON output (MCP attach) | `claw browser launch --force --json` |
| Verify port open | `claw browser verify --port 9222` |
| Stop by port (+ cleanup) | `claw browser stop --port 9222 --cleanup` |
| Stop by PID | `claw browser stop --pid 12840` |
| MCP args after launch | `["chrome-devtools-mcp@latest", "--browserUrl=http://127.0.0.1:9222"]` |
