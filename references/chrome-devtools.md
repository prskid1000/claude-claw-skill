# Chrome DevTools MCP — Browser Launch Reference

## Contents

- **AUTOMATE browser** — Chrome DevTools MCP
  - [Critical rules (debug port, `--user-data-dir` gotcha)](#critical-rules)
  - [Edge — default profile (preserves cookies/logins)](#edge--default-profile)
  - [Edge — isolated profile (no kill needed)](#edge--isolated-profile)
  - [Chrome — same flags, different binary](#chrome)
  - [Verification (`/json/version` check)](#verification)
  - [Quick reference (kill / verify / MCP args)](#quick-reference)

> Examples: [examples/chrome-devtools.md](../examples/chrome-devtools.md) · install via [setup.md](setup.md#4-mcp-servers)

---

## Critical Rules

1. **The browser MUST be launched with `--remote-debugging-port=9222`.** You cannot enable the debug port on an already-running browser.
2. **Always pass `--user-data-dir`.** Without it, if any other browser process is already running, the new launch silently attaches to the existing instance and the flag is ignored — port 9222 never opens. This is the single most common failure mode.
3. **Default profile requires killing all existing browser processes first** — the data dir is locked while any process holds it. Background tabs and the system-tray helper count.
4. **PowerShell**: a quoted path is a string, not a command. Prefix with `&` to invoke. From bash this isn't needed — quote the path normally.
5. **Verify before retrying MCP calls.** If `list_pages` returns a connection error, the port isn't open. Fix the launch — don't re-call the MCP tool.

---

## Edge — Default Profile

Use this when the user needs their existing cookies, logins, and extensions.

```bash
# 1. Kill ALL Edge processes (tabs, helpers, tray app)
taskkill //F //IM msedge.exe

# 2. Launch with the default profile path
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:/Users/$USER/AppData/Local/Microsoft/Edge/User Data" &
```

Default profile path: `C:\Users\<user>\AppData\Local\Microsoft\Edge\User Data`

---

## Edge — Isolated Profile

Use this when no logins are needed (faster, no need to kill anything).

```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:/temp/edge-debug" &
```

The `C:/temp/edge-debug` directory is created automatically.

---

## Chrome

Same flags, different binary:

```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:/temp/chrome-debug" &
```

For default profile: `C:\Users\<user>\AppData\Local\Google\Chrome\User Data`

---

## Verification

```bash
curl -s http://127.0.0.1:9222/json/version
```

Success returns JSON with `Browser`, `webSocketDebuggerUrl`, etc. Exit code 7 = port not open (browser didn't launch with the flag, or attached to existing instance — see Critical Rule #2).

---

## Quick Reference

| Task | Command |
|------|---------|
| Kill all Edge | `taskkill //F //IM msedge.exe` |
| Kill all Chrome | `taskkill //F //IM chrome.exe` |
| Verify port | `curl -s http://127.0.0.1:9222/json/version` |
| MCP plugin args | `["chrome-devtools-mcp@latest", "--browserUrl=http://127.0.0.1:9222"]` |
| PowerShell invoke | `& "C:\path\to\msedge.exe" --remote-debugging-port=9222` |
