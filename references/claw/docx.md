# `claw docx` — Word Operations Reference

> Source directory: [scripts/claw/src/claw/docx/](../../scripts/claw/src/claw/docx/)

CLI wrapper over `python-docx` (plus pandoc for markdown ingestion). Authoring and light editing of `.docx` files.

## Contents

- **CREATE a document**
  - [New blank doc](#11-new) · [Markdown → docx](#12-from-md)
- **READ / INSPECT**
  - [Extract text / structure](#21-read) · [Dump comments](#22-comments) · [Show tracked revisions](#23-diff)
- **EDIT body content**
  - [Headings](#31-add-heading) · [Paragraphs](#32-add-paragraph) · [Tables](#33-add-table) · [Images](#34-add-image) · [Insert page break](#35-insert) · [Hyperlinks](#36-hyperlink)
- **FORMAT / STYLE**
  - [Define / apply styles](#41-style) · [Sections (orientation, columns)](#42-section) · [Headers](#43-header) · [Footers](#44-footer) · [Table of contents](#45-toc)
- **META**
  - [Core / custom properties](#51-meta) · [Attach custom XML](#52-custom-xml)

---

## 1. CREATE

### 1.1 `new`
Create a blank `.docx`.
```bash
claw docx new <OUT_DOCX> [--template FILE.docx] [--force]
```

### 1.2 `from-md`
Convert Markdown (file or stdin) to .docx using pandoc.
```bash
claw docx from-md <OUT_DOCX> --data <FILE.md> [--force]
```

---

## 2. READ / INSPECT

### 2.1 `read`
Extract text, JSON, tables, or heading outline.
```bash
claw docx read <SRC_DOCX> [--text|--json|--tables|--headings]
```

### 2.2 `comments`
Comment-review operations.
```bash
claw docx comments list <SRC_DOCX> [--json]
```

### 2.3 `diff`
Emit a list of tracked insertions and deletions.
```bash
claw docx diff <SRC_DOCX> [--json]
```

---

## 3. EDIT

### 3.1 `add-heading`
Append a heading or insert one at an anchor paragraph.
```bash
claw docx add-heading <SRC_DOCX> --text <TEXT> [--level N] [--force]
```

### 3.2 `add-paragraph`
Add a paragraph with optional formatting.
```bash
claw docx add-paragraph <SRC_DOCX> --text <TEXT> [--bold] [--italic] [--force]
```

### 3.3 `add-table`
Insert a table in the document from CSV or JSON rows.
```bash
claw docx add-table <SRC_DOCX> --data <FILE.csv|.json> [--header] [--force]
```

### 3.4 `add-image`
Insert an inline image.
```bash
claw docx add-image <SRC_DOCX> --image <FILE.png|.jpg> [--width FLOAT] [--force]
```

### 3.5 `insert`
Structural insertions (pagebreak, ...).
```bash
claw docx insert pagebreak <SRC_DOCX> [--before <TEXT>] [--after <TEXT>] [--force]
```

### 3.6 `hyperlink`
Hyperlink operations.
```bash
claw docx hyperlink add <SRC_DOCX> --text <MATCH_TEXT> --url <URL> [--force]
```

---

## 4. FORMAT / STYLE

### 4.1 `style`
Define or apply paragraph / character styles.
```bash
claw docx style apply <SRC_DOCX> --name <STYLE_NAME> [--to <TEXT>] [--all-matching-style <NAME>] [--force]
claw docx style define <SRC_DOCX> --name <NAME> ... [--force]
```

### 4.2 `section`
Section operations (layout, orientation).
```bash
claw docx section add <SRC_DOCX> [--orientation portrait|landscape] [--force]
```

### 4.3 `header`
Set the header text for a section.
```bash
claw docx header <SRC_DOCX> --text <TEXT> [--force]
```

### 4.4 `footer`
Set the footer text on a section.
```bash
claw docx footer <SRC_DOCX> --text <TEXT> [--force]
```

### 4.5 `toc`
Insert a TOC field (Word recomputes on open).
```bash
claw docx toc <SRC_DOCX> [--force]
```

---

## 5. META

### 5.1 `meta`
Get / set core document properties.
```bash
claw docx meta <get|set> <SRC_DOCX> ...
```

### 5.2 `custom-xml`
Attach / inspect custom XML parts on the OPC package.
```bash
claw docx custom-xml attach <SRC_DOCX> --part <FILE.xml> [--force]
```
