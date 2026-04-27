# `claw html` — HTML Operations Reference

CLI wrapper over `BeautifulSoup4` and `lxml.html` for robust tree manipulation and data extraction.

## Contents

- **QUERY / EXTRACT**
  - [CSS/XPath Selection](#11-select) · [Clean Text Extraction](#12-text)
- **TREE MANIPULATION**
  - [Strip Elements](#21-strip) · [Unwrap Tags](#22-unwrap) · [Wrap Elements](#23-wrap) · [Replace Elements](#24-replace)
- **ADVANCED / CLEANUP**
  - [Sanitize HTML](#31-sanitize) · [Absolutize URLs](#32-absolutize) · [Rewrite Links](#33-rewrite) · [Format HTML](#34-fmt) · [Diagnose Parsers](#35-diagnose)

---

## Critical Rules

1. **Parser Consistency** — Use `diagnose` if you notice unexpected tree structures; different parsers handle broken HTML differently.
2. **Sanitization** — The `sanitize` command uses an allow-list approach. It is effective for general cleanup but should be combined with other measures for high-security environments.
3. **URL Rewriting** — `absolutize` requires a valid `--base` URL to correctly resolve relative paths.
4. **Encoding** — Output is UTF-8 by default; ensure your environment supports Unicode characters.

---

## 1.1 select
Query HTML with CSS selectors or XPath expressions.
```bash
claw html select <SRC> [--css <SELECTOR>|--xpath <PATH>] [--text|--attr <NAME>]
```

## 1.2 text
Extract flattened, clean text content from the document (removes boilerplate).
```bash
claw html text <SRC> [--json] [--include-links]
```

---

## 2.1 strip
Remove matched elements and their children from the tree.
```bash
claw html strip <SRC> --css <SELECTOR> -o <OUT> [--force]
```

## 2.2 unwrap
Remove the tag of matched elements but preserve their inner content.
```bash
claw html unwrap <SRC> --css <SELECTOR> -o <OUT> [--force]
```

## 2.3 wrap
Wrap each matched element in a new parent tag. `--with` accepts a tag spec like `tag`, `tag.class`, or `tag.a.b#id`.
```bash
claw html wrap <SRC> (--css <SELECTOR> | --xpath <PATH>) --with <TAG_SPEC> (--in-place | --out <PATH>)
```

## 2.4 replace
Replace matched elements (`tag.replace_with(...)`). Pick exactly one source: `--text` for literal text, `--html` for an inline HTML fragment, or `--with-file` to read the fragment from disk.
```bash
claw html replace <SRC> (--css <SELECTOR> | --xpath <PATH>) (--text <TEXT> | --html <FRAGMENT> | --with-file <PATH>) (--in-place | --out <PATH>)
```

---

## 3.1 sanitize
Strip scripts, styles, and dangerous attributes using an allow-list.
```bash
claw html sanitize <SRC> -o <OUT> [--force]
```

## 3.2 absolutize
Convert relative URLs to absolute form using a base URL.
```bash
claw html absolutize <SRC> --base <URL> -o <OUT> [--force]
```

## 3.3 rewrite
Rewrite URL substrings across link-bearing attributes. `--from` is the substring to match; `--to` is the replacement. By default, `lxml`'s default link-bearing attrs are scanned — override with `--attrs` (comma-separated).
```bash
claw html rewrite <SRC> --from <STR> --to <STR> [--attrs href,src,...] (--in-place | --out <PATH>)
```

## 3.4 fmt
Prettify or minify the HTML structure.
```bash
claw html fmt <SRC> [--minify] -o <OUT> [--force]
```

## 3.5 diagnose
Display how different underlying parsers interpret the provided HTML.
```bash
claw html diagnose <SRC>
```

---

## Footguns
- **Malformed Input** — Malformed HTML (e.g., unclosed tags) may be repaired differently by `lxml` than by a browser's engine.
- **Script Stripping** — `sanitize` removes `<script>` tags but may miss sophisticated obfuscated event handlers if they are not in the standard allow-list.

## Escape Hatch
Underlying library: `BeautifulSoup4` (Python) with `lxml` backend. For high-speed stream processing, consider `selectolax`.

## Quick Reference
| Task | Command |
|------|---------|
| Extract Text | `claw html text index.html` |
| Remove Scripts | `claw html strip index.html --css "script"` |
| Get Alt Text | `claw html select index.html --css "img" --attr alt` |
| Prettify HTML | `claw html fmt index.html -o pretty.html` |
| Clean Links | `claw html absolutize raw.html --base "https://abc.com"` |
