# `claw docx` — Word Operations Reference

CLI wrapper over `python-docx` (plus pandoc for markdown ingestion). Authoring and light editing of `.docx` files.

## Contents

- **CREATE a document**
  - [New blank doc](#11-new) · [Markdown → docx](#12-from-md)
- **READ / INSPECT**
  - [Extract text / structure](#21-read) · [Dump comments](#22-comments) · [Show tracked revisions](#23-diff)
- **EDIT body content**
  - [Headings](#31-add-heading) · [Paragraphs](#32-add-paragraph) · [Tables](#33-add-table) · [Images](#34-add-image) · [Insert page break](#35-insert) · [Hyperlinks](#36-hyperlink)
- **FORMAT / STYLE**
  - [Define / apply styles](#41-style) · [Sections (orientation, columns)](#42-section) · [Headers](#43-header) · [Footers](#44-footer) · [Table of contents](#45-toc) · [Table column fitting](#46-table-fit)
- **META**
  - [Core / custom properties](#51-meta) · [Attach custom XML](#52-custom-xml)

---

## Critical Rules

1. **TOC Updates** — The `toc` command inserts a field code. Word will prompt to "Update Table" when the file is first opened.
2. **Style Availability** — `style apply` requires the style name to exist in the document's style gallery or template.
3. **Pandoc Dependency** — `from-md` requires `pandoc` to be installed and available in the system PATH.
4. **Table Fitting** — Use `table-fit` after `add-table` if column widths appear inconsistent.

---

## 1.1 new
Create a blank `.docx`.
```bash
claw docx new <OUT_DOCX> [--template FILE.docx] [--force]
```

## 1.2 from-md
Convert Markdown (file or stdin) to .docx using pandoc.
```bash
claw docx from-md <OUT_DOCX> --data <FILE.md> [--force]
```

---

## 2.1 read
Extract text, JSON, tables, or heading outline.
```bash
claw docx read <SRC_DOCX> [--text|--json|--tables|--headings]
```

## 2.2 comments
Comment-review operations.
```bash
claw docx comments list <SRC_DOCX> [--json]
```

## 2.3 diff
Emit a list of tracked insertions and deletions (revisions).
```bash
claw docx diff <SRC_DOCX> [--json]
```

---

## 3.1 add-heading
Append a heading or insert one at an anchor paragraph.
```bash
claw docx add-heading <SRC_DOCX> --text <TEXT> [--level N] [--force]
```

## 3.2 add-paragraph
Add a paragraph with optional formatting.
```bash
claw docx add-paragraph <SRC_DOCX> --text <TEXT> [--bold] [--italic] [--force]
```

## 3.3 add-table
Insert a table in the document from CSV or JSON rows.
```bash
claw docx add-table <SRC_DOCX> --data <FILE.csv|.json> [--header] [--force]
```

## 3.4 add-image
Insert an inline image.
```bash
claw docx add-image <SRC_DOCX> --image <FILE.png|.jpg> [--width FLOAT] [--force]
```

## 3.5 insert
Structural insertions like pagebreaks.
```bash
claw docx insert pagebreak <SRC_DOCX> [--before <TEXT>] [--after <TEXT>] [--force]
```

## 3.6 hyperlink
Add or modify hyperlinks.
```bash
claw docx hyperlink add <SRC_DOCX> --text <MATCH_TEXT> --url <URL> [--force]
```

---

## 4.1 style
Define or apply paragraph / character styles.
```bash
claw docx style apply <SRC_DOCX> --name <STYLE_NAME> [--to <TEXT>] [--all-matching-style <NAME>] [--force]
claw docx style define <SRC_DOCX> --name <NAME> [--font <NAME>] [--size <PT>] [--force]
```

## 4.2 section
Section operations (layout, orientation, columns).
```bash
claw docx section add <SRC_DOCX> [--orientation portrait|landscape] [--cols N] [--force]
```

## 4.3 header
Set the header text for the current section.
```bash
claw docx header <SRC_DOCX> --text <TEXT> [--force]
```

## 4.4 footer
Set the footer text for the current section.
```bash
claw docx footer <SRC_DOCX> --text <TEXT> [--force]
```

## 4.5 toc
Insert a Table of Contents field code.
```bash
claw docx toc <SRC_DOCX> [--force]
```

## 4.6 table-fit
Autofit table columns to content.
```bash
claw docx table-fit <SRC_DOCX> [--table-index N] [--force]
```

---

## 5.1 meta
Read or write core and custom document properties.
```bash
claw docx meta <get|set> <SRC_DOCX> [--property KEY] [--value VAL]
```

## 5.2 custom-xml
Attach or inspect custom XML parts on the OPC package.
```bash
claw docx custom-xml attach <SRC_DOCX> --part <FILE.xml> [--force]
```

---

## Footguns
- **Tracked Changes** — Tracked changes are not automatically resolved; use a specialized tool if you need to accept/reject all revisions programmatically.
- **Complex Templates** — Some advanced Word features (macros, complex content controls) may be stripped or corrupted if the underlying `python-docx` library doesn't support them.

## Escape Hatch
Underlying library: `python-docx` (Python). For lower-level manipulation of the XML structure, use `lxml` on the extracted `.docx` (ZIP) contents.

## Quick Reference Table
| Task | Command |
|------|---------|
| New Document | `claw docx new report.docx` |
| MD to Docx | `claw docx from-md report.docx --data content.md` |
| Add Heading | `claw docx add-heading report.docx --text "Title" --level 1` |
| Insert Image | `claw docx add-image report.docx --image img.png` |
| Add TOC | `claw docx toc report.docx` |
