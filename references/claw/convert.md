# `claw convert` — Format Conversion Reference

CLI wrapper over Pandoc.

## Contents
- [General](#convert) · [PDF No-LaTeX](#md2pdf-nolatex) · [Formats](#list-formats)

---

## `convert`
Convert between Markdown, DOCX, PDF, HTML, etc.
```bash
claw convert <SRC> <DST> [--toc] [--reference <FILE.docx>] [--force]
```

## `md2pdf-nolatex`
Render Markdown to PDF via PyMuPDF Story (no LaTeX required).
```bash
claw convert md2pdf-nolatex <SRC> <DST> [--force]
```

## `list-formats`
List supported Pandoc input/output formats.
```bash
claw convert list-formats [--json]
```

---

## Quick Reference
| Task | Command |
|------|---------|
| MD → DOCX | `claw convert in.md out.docx` |
| MD → PDF | `claw convert md2pdf-nolatex in.md out.pdf` |
| List Formats | `claw convert list-formats --json` |
