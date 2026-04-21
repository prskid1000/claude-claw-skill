# `claw convert` — Universal Converter Reference

CLI wrapper over Pandoc for format-to-format transformation.

## Contents

- **GENERAL**
  - [Convert formats](#11-convert) · [List supported](#12-list-formats)
- **SPECIALIZED**
  - [Markdown to PDF (No-LaTeX)](#21-md2pdf-nolatex) · [Render slides](#22-slides) · [Compose book](#23-book)

---

## Critical Rules

1. **Pandoc dependency** — Requires `pandoc` to be on the system PATH.
2. **Positional Args** — Most verbs use `SRC DST` as positional arguments.
3. **Reference Docs** — Use `--reference-doc` for Word/PPTX to inherit styles/branding.

---

## 1.1 convert
General purpose conversion between any formats supported by Pandoc.
```bash
claw convert <SRC> <DST> [--toc] [--template <FILE>] [--reference-doc <FILE>] [--force]
```

## 1.2 list-formats
Show all formats Pandoc can read and write on this system.
```bash
claw convert list-formats [--json]
```

---

## 2.1 md2pdf-nolatex
Render Markdown to PDF using PyMuPDF (no LaTeX engine required).
```bash
claw convert md2pdf-nolatex <SRC> <DST> [--css <FILE>] [--force]
```

## 2.2 slides
Convert Markdown to presentation formats (reveal.js, Beamer, PPTX).
```bash
claw convert slides <SRC.md> --format <reveal|beamer|pptx> [-o OUT] [--force]
```

## 2.3 book
Concatenate multiple chapters into a single PDF/EPUB/DOCX/HTML output.
```bash
claw convert book <CHAPTERS...> -o <OUT> [--csl <FILE>] [--bib <FILE>] [--force]
```

---

## Footguns
- **Table Formatting** — Pandoc sometimes struggles with complex nested tables in Markdown → Word.
- **Math** — No-LaTeX PDF mode does not support complex LaTeX math blocks.

## Escape Hatch
- [Pandoc User Guide](https://pandoc.org/MANUAL.html)

---

## Quick Reference
| Task | Command |
|------|---------|
| MD to DOCX | `claw convert in.md out.docx` |
| MD to PDF (Light) | `claw convert md2pdf-nolatex in.md out.pdf` |
| Build Book | `claw convert book ch1.md ch2.md -o book.epub` |
| List Formats | `claw convert list-formats` |
