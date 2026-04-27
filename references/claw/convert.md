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
3. **Reference Docs** — Use `--ref-doc` for Word/PPTX to inherit styles/branding.
4. **Nested verb name** — `convert` is also a subcommand: invoke as `claw convert convert <SRC> <DST>`.

---

## 1.1 convert
General purpose conversion between any formats supported by Pandoc. Note the nested `convert convert` form.
```bash
claw convert convert <SRC> <DST> [--from <FMT>] [--to <FMT>] [-s|--standalone] [--embed-resources] [--toc] [--toc-depth N] [--template <FILE>] [--ref-doc <FILE>] [--css <FILE>] [--mathjax] [--katex] [--citeproc] [--bib <FILE>] [--csl <FILE>] [--engine xelatex|lualatex|pdflatex|weasyprint|typst|tectonic] [--highlight-style <NAME>] [--number-sections] [--metadata K=V] [--variable K=V] [--defaults <YAML>]
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
claw convert slides <SRC.md> --format <reveal|beamer|pptx> --out <PATH> [--theme <NAME>] [--ref-doc <FILE>] [--slide-level N]
```

## 2.3 book
Concatenate multiple chapters into a single PDF/EPUB/DOCX/HTML output.
```bash
claw convert book <CHAPTERS...> --out <PATH> [--title <TEXT>] [--author <TEXT>] [--metadata K=V] [--toc] [--toc-depth N] [--csl <FILE>] [--bib <FILE>] [--css <FILE>] [--engine <NAME>] [--ref-doc <FILE>] [--cover <IMG>] [--stream]
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
| MD to DOCX | `claw convert convert in.md out.docx` |
| MD to PDF (Light) | `claw convert md2pdf-nolatex in.md out.pdf` |
| Build Book | `claw convert book ch1.md ch2.md --out book.epub` |
| List Formats | `claw convert list-formats` |
