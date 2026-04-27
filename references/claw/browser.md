# `claw browser` — Browser Automation Reference

CLI wrapper for launching Chrome/Edge with remote debugging enabled for MCP tools.

## Contents

- **LIFECYCLE**
  - [Launch browser](#11-launch) · [Stop browser](#12-stop)
- **DIAGNOSTICS**
  - [Verify connection](#21-verify)

---

## Critical Rules

1. **Port** — Defaults to `9222`. Ensure this port is not blocked by a firewall.
2. **Profile** — Use `--profile throwaway` for clean, isolated sessions (auto-deleted on stop).
3. **Headless** — Defaults to headed mode for visibility; use `--headless` for background ops.

---

## 1.1 launch
Start a browser instance with remote debugging active.
```bash
claw browser launch [--browser chrome|edge] [--port 9222] [--profile default|throwaway] [--user-data-dir <PATH>] [--browser-path <EXE>] [--kill-existing] [--timeout <SEC>]
```

## 1.2 stop
Terminate browser debug processes by port, PID, or sweep all matching browsers.
```bash
claw browser stop [--port 9222] [--pid <PID>] [--all] [--browser edge|chrome|both] [--cleanup]
```

---

## 2.1 verify
Check if the Chrome DevTools protocol is responding on the specified port.
```bash
claw browser verify [--port 9222] [--timeout <SEC>]
```

---

## Footguns
- **Port Conflicts** — Only one browser can own port 9222. `launch` will fail if another instance is running.
- **Zombie Processes** — If the CLI is hard-killed, the browser might stay open. Use `stop` to clean up.

## Escape Hatch
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/) · [Playwright Docs](https://playwright.dev/)

---

## Quick Reference
| Task | Command |
|------|---------|
| Launch Chrome | `claw browser launch` |
| Launch Edge | `claw browser launch --browser edge` |
| isolated session | `claw browser launch --profile throwaway` |
| Stop Browser | `claw browser stop` |
