# `claw html` — HTML Select / Mutate / Clean Reference

CLI wrapper around BeautifulSoup4 (with `lxml` as parser). Every verb takes HTML on stdin or from a file and emits transformed HTML on stdout, so `claw html` composes well in shell pipelines.

Library API for escape hatches: [references/web-parsing.md § BeautifulSoup4](../web-parsing.md#beautifulsoup4) and [§ lxml.html](../web-parsing.md#lxmlhtml).

## Contents

- **SELECT / QUERY elements**
  - [CSS or XPath select (htmlq-style)](#11-select) · [Extract text content](#12-text)
- **MUTATE the tree**
  - [Strip (decompose)](#21-strip) · [Unwrap (remove tag, keep children)](#22-unwrap) · [Wrap in new parent](#23-wrap) · [Replace content](#24-replace)
- **SANITIZE**
  - [Allow-list tags / attrs](#31-sanitize)
- **REWRITE links / URLs**
  - [Absolutize relative URLs](#41-absolutize) · [Rewrite URL substrings](#42-rewrite)
- **FORMAT output**
  - [Pretty-print with different formatters](#51-fmt)
- **DIAGNOSE parser behavior**
  - [Compare parsers side-by-side](#61-diagnose)
- **When `claw html` isn't enough** — [escape hatches](#when-claw-isnt-enough)

---

## Critical Rules

1. **Functional by default** — `claw html` does not mutate the input file. Every verb reads HTML from `<file|->` and writes transformed HTML to `--out FILE` (or stdout). To modify in place, use `--in-place` explicitly; atomic temp-file + rename applies. `--backup` keeps `<file>.bak`.
2. **Selectors auto-detect** — `--css "..."` and `--xpath "..."` both work. Without `--css` / `--xpath`, `claw` inspects the selector: leading `/` or `//` → XPath, else CSS.
3. **Stream model: stdin → stdout** — pass `-` as the positional file to read from stdin. Omit `--out` to write to stdout. This lets you compose: `claw web fetch URL --out - | claw html strip --css "script,style" | claw html text -`.
4. **Structured output** — `select` and `text` can emit `--json` (array of match records). Mutation verbs emit transformed HTML by default; `--json` on them returns `{input_bytes, output_bytes, matches_affected}`. Errors under `--json` emit `{error, code, hint, doc_url}` to stderr.
5. **Exit codes** — `0` success, `1` generic, `2` usage error (bad selector syntax), `3` partial (some selector matched 0 elements in multi-selector call), `4` bad input (non-HTML), `5` system error, `130` SIGINT.
6. **Help** — `claw html --help`, `claw html <verb> --help`, `--examples` prints runnable recipes.
7. **Parser** — default is `lxml` (fast, lenient). Override with `--parser html.parser` (stdlib) or `--parser html5lib` (browser-faithful). See [§6.1 `diagnose`](#61-diagnose) to pick the right one.
8. **Security** — `claw html sanitize` uses BeautifulSoup tree manipulation on an allow-list model, NOT `lxml.html.clean`. The latter is explicitly flagged by its maintainer as unsafe for untrusted HTML. For security-critical sanitization of attacker-controlled input, use `bleach` in Python directly — `claw html sanitize` is a convenience, not a security boundary.

---

## 1. SELECT / QUERY

### 1.1 `select`

Query the tree with CSS or XPath (htmlq-style).

```
claw html select <file|-> (--css EXPR | --xpath EXPR)
                          [--all | --index N]
                          [--attr NAME | --text | --html]
                          [--sep "\n"] [--json]
                          [--out FILE|-]
```

Flags:

- `--all` — emit all matches (default).
- `--index N` — emit only the N-th match (1-based).
- `--attr NAME` — print the value of the named attribute. Mutually exclusive with `--text`/`--html`.
- `--text` — print text content (equivalent to `.get_text()`).
- `--html` — print the outer HTML of each match (default).
- `--sep` — join multiple outputs (default `\n`).

Examples:

```
claw html select page.html --css "article h2 > a" --attr href
```

```
claw html select page.html --css "table.prices" --html --out prices.html
```

```
claw html select page.html --xpath "//meta[@property='og:image']/@content"
```

### 1.2 `text`

Extract flattened text content from an entire document or a subtree.

```
claw html text <file|-> [--css EXPR | --xpath EXPR]
                        [--sep "\n"] [--strip]
                        [--out FILE|-]
```

Flags:

- `--strip` — equivalent to BeautifulSoup's `get_text(strip=True)`; collapse whitespace and trim each string.
- `--sep` — separator between navigable strings.

Examples:

```
claw html text article.html --strip
```

```
claw html text page.html --css "main" --sep " " --strip
```

---

## 2. MUTATE

### 2.1 `strip`

Remove matched elements from the tree (`decompose()`). Keeps the rest of the document.

```
claw html strip <file|-> (--css EXPR | --xpath EXPR)...
                         [--in-place] [--backup] [--out FILE|-]
```

Flags:

- `--css` / `--xpath` — repeatable. `--css "script,style,nav"` or three separate `--css` flags both work.

Examples:

```
claw html strip page.html --css "script,style,nav,.advert" --out clean.html
```

```
claw web fetch URL --out - | claw html strip - --css "script,style" | claw html text -
```

### 2.2 `unwrap`

Replace matched elements with their children (keeps content, removes the wrapper tag).

```
claw html unwrap <file|-> (--css EXPR | --xpath EXPR)
                          [--in-place] [--out FILE|-]
```

Use case: `<span class="marker">content</span>` → `content`.

Example:

```
claw html unwrap page.html --css "span.marker,font" --out clean.html
```

### 2.3 `wrap`

Wrap each matched element in a new parent.

```
claw html wrap <file|-> (--css EXPR | --xpath EXPR) --with "TAG.class#id"
                        [--in-place] [--out FILE|-]
```

Flags:

- `--with "TAG.class#id"` — tiny selector dialect: `div` / `div.scroll` / `div.scroll#main`. Multiple classes with `.a.b`.

Example:

```
claw html wrap doc.html --css "table" --with "div.scroll-x" --out doc-responsive.html
```

### 2.4 `replace`

Replace matched elements with new text or HTML.

```
claw html replace <file|-> (--css EXPR | --xpath EXPR)
                           (--text STR | --html STR | --with-file FILE)
                           [--in-place] [--out FILE|-]
```

Example:

```
claw html replace page.html --css ".placeholder" --text "TBD"
```

```
claw html replace template.html --css "#body" --with-file rendered-body.html
```

---

## 3. SANITIZE

### 3.1 `sanitize`

Allow-list-based cleanup. Default ruleset removes `<script>`, `<style>`, `<iframe>`, `<object>`, `<embed>`, inline event handlers, and `javascript:` URLs.

```
claw html sanitize <file|-> [--allow TAG[,TAG...]] [--allow-attr ATTR[,ATTR...]]
                            [--remove scripts,iframes,style,comments,forms,embeds]
                            [--strip-unknown]
                            [--in-place] [--out FILE|-]
```

Flags:

- `--allow` — add tags to the default allow-list. Anything NOT in the allow-list gets unwrapped (children preserved).
- `--allow-attr` — whitelist attributes (default: `href src alt title class id`).
- `--remove` — explicitly remove categories (default: `scripts,iframes,style,forms,embeds`).
- `--strip-unknown` — unknown tags are decomposed (removed entirely, not just unwrapped).

> **Security warning** — for untrusted input destined for a browser that runs in the same origin as sensitive data, use `bleach` directly. `claw html sanitize` is a pragmatic cleanup tool, not a security boundary against determined XSS payloads. See the Critical Rules note above.

Examples:

```
claw html sanitize user-input.html --allow "b,i,a,p,br" \
  --allow-attr "href,title" --strip-unknown --out safe.html
```

```
claw html sanitize scraped.html --remove scripts,iframes,forms --out clean.html
```

---

## 4. REWRITE

### 4.1 `absolutize`

Resolve relative links against a base URL.

```
claw html absolutize <file|-> --base URL [--attrs href,src,action]
                              [--in-place] [--out FILE|-]
```

Default attrs: `href,src,action,poster,srcset`.

Example:

```
claw html absolutize scraped.html --base https://example.com/docs/ \
  --out absolute.html
```

### 4.2 `rewrite`

Find-and-replace URL substrings across link-bearing attributes.

```
claw html rewrite <file|-> --from URL --to URL [--attrs href,src]
                           [--in-place] [--out FILE|-]
```

Example:

```
claw html rewrite page.html --from "http://old.example.com" --to "https://new.example.com"
```

---

## 5. FORMAT

### 5.1 `fmt`

Pretty-print the HTML.

```
claw html fmt <file|-> [--formatter minimal|html|html5|none]
                       [--indent 2] [--in-place] [--out FILE|-]
```

Flags:

- `--formatter minimal` (default) — encode only necessary characters.
- `--formatter html` — HTML entity encoding for every non-ASCII character.
- `--formatter html5` — void elements (`<br>`, `<img>`) without self-closing slash.
- `--formatter none` — no entity encoding at all (use with care).

Example:

```
claw html fmt messy.html --formatter html5 --indent 4 --out clean.html
```

---

## 6. DIAGNOSE

### 6.1 `diagnose`

Show how each installed parser interprets the document. Useful when `lxml` and `html5lib` disagree (fragile markup).

```
claw html diagnose <file|-> [--json]
```

Output: one section per parser (`lxml`, `html.parser`, `html5lib`) with the resulting pretty-printed tree, parse time, and any warnings.

Example:

```
claw html diagnose suspicious.html | less
```

---

## When `claw html` Isn't Enough

Drop into BeautifulSoup / lxml directly:

| Use case | Why `claw` can't do it | Library anchor |
|---|---|---|
| Complex tree walks (conditional mutation based on siblings / ancestors) | CLI flag surface can't express control flow | [web-parsing.md § BeautifulSoup4 Navigation](../web-parsing.md#navigation) |
| Custom parser with `SoupStrainer` for memory-bounded scraping | No flag to configure parse filter | [web-parsing.md § SoupStrainer](../web-parsing.md#soupstrainer-partial-parsing) |
| HTML diff / annotate | Out of scope | [web-parsing.md § HTML diff](../web-parsing.md#html-diff) |
| Form filling via `lxml.html` | Not wrapped | [web-parsing.md § Forms](../web-parsing.md#forms) |
| Multi-valued attribute control | Fixed default | [web-parsing.md § Multi-valued Attributes](../web-parsing.md#multi-valued-attributes) |
| Production-grade XSS sanitization of user input | `sanitize` is convenience, not a security boundary | Use `bleach` (allow-list-based, maintained for security) directly |
| iterparse-style streaming | BeautifulSoup loads the whole tree | [web-parsing.md § iterparse](../web-parsing.md#iterparse-streaming) on `lxml` |

## Footguns

- **`decompose()` zombie references** — mutating verbs in `claw` use a functional transform (read → transform → write) specifically to avoid BeautifulSoup's `decompose()` zombie-object issue. If you script in Python, don't hold references to decomposed tags.
- **Selector precedence** — `--css "script,style"` is one selector matching either tag; `--css script --css style` is two selectors. Both work; the former is slightly faster.
- **`sanitize` allow-list semantics** — tags not in the allow-list get **unwrapped** (children kept) by default. To drop them entirely, add `--strip-unknown`.
- **`html5lib` slowness** — `--parser html5lib` is 3–10× slower than `lxml`. Only use when exact browser parity matters (or when `diagnose` shows `lxml` getting it wrong).
- **`absolutize` doesn't touch `srcset` values' widths** — it rewrites each URL token but preserves the `1x`/`2x` size descriptors.
- **XPath in a lenient HTML parser** — `lxml.html` builds an ElementTree that supports XPath natively. BeautifulSoup (the default) does NOT; `claw` transparently switches to the `lxml` parser when `--xpath` is used. If you also passed `--parser html5lib`, that switch overrides your preference.

---

## Quick Reference

| Task | One-liner |
|------|-----------|
| Select all links | `claw html select f.html --css "a" --attr href` |
| Extract title | `claw html select f.html --css "title" --text --index 1` |
| Strip scripts & style | `claw html strip f.html --css "script,style" --out clean.html` |
| Plain text | `claw html text f.html --strip` |
| Unwrap `<span>`s | `claw html unwrap f.html --css "span"` |
| Wrap tables in scroll divs | `claw html wrap f.html --css "table" --with "div.scroll"` |
| Sanitize user HTML | `claw html sanitize in.html --allow "b,i,a,p" --strip-unknown` |
| Make links absolute | `claw html absolutize f.html --base https://example.com/` |
| Rewrite host | `claw html rewrite f.html --from http://old --to https://new` |
| Pretty-print | `claw html fmt f.html --formatter html5` |
| Pipe from fetch | `claw web fetch URL --out - \| claw html text - --strip` |
