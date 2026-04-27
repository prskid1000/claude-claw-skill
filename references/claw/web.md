# `claw web` — Web Fetch / Extract Reference

CLI wrapper over `trafilatura` and `httpx` for article extraction and robust fetching.

## Contents

- **FETCH**
  - [Download page](#11-fetch) · [Capture snapshot](#12-snapshot)
- **EXTRACT**
  - [Article text](#21-extract) · [Find links](#22-links) · [Extract tables](#23-table)

---

## Critical Rules

1. **User Agent** — Defaults to a browser-like agent to avoid blocks.
2. **Retries** — Built-in exponential backoff for transient 5xx errors.
3. **Structured Extraction** — `extract` specifically targets article content, discarding ads/navigation.

---

## 1.1 fetch
HTTP GET/POST a URL; write body to `--out` (or stdout). Supports custom method/headers/body, retries with `--retry-on`, cookie jars, proxy, and on-the-fly content extraction via `--format` + optional `--selector`.
```bash
claw web fetch <URL> [--out <PATH|->] [--method get|post|...] [--header K=V]... [--data TEXT|@FILE] [--timeout FLOAT] [--retries N] [--retry-on 5xx,429,timeout,...] [--save-cookies PATH] [--load-cookies PATH] [--ua TEXT] [--proxy URL] [--format text|html|markdown|json] [--selector CSS]
```

## 1.2 snapshot
Save a permanent copy of a page (WARC or self-contained HTML).
```bash
claw web snapshot <URL> -o <OUT> [--force]
```

---

## 2.1 extract
Extract clean article text using trafilatura.
```bash
claw web extract <URL|FILE> [--json] [--include-comments]
```

## 2.2 links
Enumerate `<a href=...>` from a URL, file, or stdin. Use `--absolute` (with optional `--base`) to resolve relative URLs, `--same-origin` to keep only the host's own links, `--unique` to de-dupe by absolute URL, and `--filter` for predicate filtering (e.g. `"href contains 'docs'"`).
```bash
claw web links <SRC> [--absolute] [--base <URL>] [--filter <EXPR>] [--same-origin] [--unique] [--format text|json] [--out <PATH>]
```

## 2.3 table
Extract structured data from `<table>` elements as JSON/CSV.
```bash
claw web table <URL|FILE> [--css <SELECTOR>] [--json|--csv]
```

---

## Footguns
- **Dynamic Content** — `claw web` does not execute JavaScript. Use `claw browser` for SPA/React sites.
- **Extraction Failures** — Trafilatura might fail on non-article pages (e.g., login screens, dashboards).

## Escape Hatch
- [trafilatura docs](https://trafilatura.readthedocs.io/) · [httpx docs](https://www.python-httpx.org/)

---

## Quick Reference
| Task | Command |
|------|---------|
| Extract Article | `claw web extract https://example.com/news` |
| List Links | `claw web links index.html --json` |
| Get Tables | `claw web table https://site.com/stats` |
| Raw Fetch | `claw web fetch URL --json` |
