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
Download raw HTML or content with headers and cookies.
```bash
claw web fetch <URL|FILE> [--json] [--cache]
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
Extract all URLs found in a document.
```bash
claw web links <URL|FILE> [--internal|--external] [--json]
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
