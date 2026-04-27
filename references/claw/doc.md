# `claw doc` — Google Docs Operations Reference

CLI wrapper over the Google Docs API. Handles document creation, content manipulation, and multi-format exports.

## Contents

- **CREATE / READ**
  - [Create Document](#11-create) · [Read Content](#12-read)
- **EDIT / MANIPULATE**
  - [Append Content](#21-append) · [Build from Markdown](#22-build) · [Search and Replace](#23-replace)
- **EXPORT / MANAGE**
  - [Multi-format Export](#31-export) · [Manage Tabs](#32-tabs)

---

## Critical Rules

1. **Authentication** — Requires valid Google Workspace (GWS) credentials configured in the environment.
2. **Document ID** — Use the unique ID from the document URL (e.g., `1aBcDe...`), not the file name.
3. **Markdown Sync** — `build` replaces existing content with the structure defined in your Markdown file.
4. **Rate Limits** — The Google Docs API has per-minute quotas. `claw` automatically handles simple retries, but avoid extremely high-frequency edits.

---

## 1.1 create
Create a new, blank Google Doc (optionally seeded from a markdown file).
```bash
claw doc create --title <TITLE> [--from <FILE.md>] [--parent <FOLDER_ID>] [--share <SPEC>] [--tab <ID>]
```

## 1.2 read
Extract the document's content as plain text, JSON structure, or markdown.
```bash
claw doc read <DOC_ID> [--format text|json|md] [--out <PATH>] [--tab <ID>]
```

---

## 2.1 append
Append text or markdown content to the end of the document.
```bash
claw doc append <DOC_ID> [--from <FILE>] [--text <TEXT>] [--tab <ID>] [--chunk-size N]
```

## 2.2 build
Apply a markdown file to an existing Doc (replaces content by default).
```bash
claw doc build <DOC_ID> --from <FILE.md> [--append] [--replace-all] [--force-clear] [--tab <ID>] [--from-index N] [--chunk-size N]
```

## 2.3 replace
Perform a find-and-replace operation on literal text strings.
```bash
claw doc replace <DOC_ID> --find <STR> --with <STR> [--match-case] [--tab <ID>]
```

---

## 3.1 export
Download a Google Doc in a specific local format.
```bash
claw doc export <DOC_ID> --as <pdf|docx|html|md|txt|epub|odt|rtf> --out <PATH>
```

## 3.2 tabs
Subgroup of tab operations on Docs that use the tabs feature.
```bash
claw doc tabs list <DOC_ID>
```

---

## Footguns
- **Lossy Exports** — Exporting to `.md` or `.txt` will strip advanced formatting, images, and comments.
- **Complex Replaces** — `replace` does not support regex; it only performs exact string matching.

## Escape Hatch
Underlying API: `Google Docs API` (v1). For complex batch requests not supported by `claw`, use the `google-api-python-client` directly.

## Quick Reference
| Task | Command |
|------|---------|
| Create New | `claw doc create --title "Project Plan"` |
| Read Text | `claw doc read 1aBcDe... --format text` |
| Append File | `claw doc append 1aBcDe... --from notes.md` |
| Export PDF | `claw doc export 1aBcDe... --as pdf --out report.pdf` |
| Swap Variable | `claw doc replace 1aBcDe... --find "{{NAME}}" --with "Alice"` |
