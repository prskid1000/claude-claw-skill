# `claw pdf` — PDF Operations Reference

CLI wrapper over PyMuPDF (fitz), pypdf, and pdfplumber. Handles creation, extraction, transformation, and security for PDF documents.

## Contents

- **CREATE**
  - [From HTML](#11-from-html) · [From Markdown](#12-from-md) · [QR Code](#13-qr) · [Barcode](#14-barcode) · [Convert from EPUB/XPS/CBZ](#15-convert)
- **READ / EXTRACT**
  - [Text](#21-extract-text) · [Tables](#22-extract-tables) · [Metadata](#23-info) · [Search](#24-search) · [OCR](#25-ocr) · [Chars](#26-chars) · [Words](#27-words) · [Shapes](#28-shapes) · [Extract images](#29-extract-images)
- **EDIT / TRANSFORM**
  - [Merge](#31-merge) · [Split](#32-split) · [Rotate](#33-rotate) · [Crop](#34-crop) · [Render to Image](#35-render) · [Watermark](#36-watermark) · [Redact](#37-redact)
- **ADVANCED**
  - [Annotate](#41-annotate) · [Attachments](#42-attach) · [Bookmarks](#43-bookmark) · [Form Fields](#44-form) · [Labels](#45-labels) · [Layers](#46-layer) · [Stamping](#47-stamp) · [Table Debugging](#48-tables-debug) · [TOC](#49-toc) · [Flatten](#410-flatten) · [Journal](#411-journal)
- **SECURITY**
  - [Encrypt/Decrypt](#51-encryptdecrypt)
- **PROPERTIES**
  - [Core metadata](#61-meta)

---

## Critical Rules

1. **OCR Dependencies** — The `ocr` command requires `tesseract-ocr` and `ghostscript` to be installed on the system.
2. **Redaction Safety** — `redact` physically removes content and cleans the underlying XREF table. Always verify on a copy.
3. **Table Extraction** — If `extract-tables` fails on a scanned document, run `ocr` first.
4. **Coordinate System** — PDF uses a bottom-left (0,0) origin by default, but `claw` transforms to top-left (0,0) for consistency with image tools.

---

## 1.1 from-html
Render HTML to PDF using a headless browser or library.
```bash
claw pdf from-html <SRC_HTML> <OUT_PDF> [--force]
```

## 1.2 from-md
Render Markdown to PDF via Pandoc or direct conversion.
```bash
claw pdf from-md <SRC_MD> <OUT_PDF> [--force]
```

## 1.3 qr
Generate a PDF containing a QR code.
```bash
claw pdf qr --value <TEXT> -o <OUT_PDF> [--size N] [--force]
```

## 1.4 barcode
Generate a PDF containing a barcode.
```bash
claw pdf barcode --type <TYPE> --value <TEXT> -o <OUT_PDF> [--force]
```

## 1.5 convert
Convert EPUB / XPS / CBZ / FB2 / OXPS into PDF via PyMuPDF.
```bash
claw pdf convert <SRC> <OUT_PDF> [--page-size A4]
```

---

## 2.1 extract-text
Extract plain text or structured JSON text from the PDF.
```bash
claw pdf extract-text <SRC_PDF> [--json] [--pages N-M]
```

## 2.2 extract-tables
Detect and extract tabular data.
```bash
claw pdf extract-tables <SRC_PDF> [--json] [--csv] [--format format]
```

## 2.3 info
Display metadata, encryption status, and page count.
```bash
claw pdf info <SRC_PDF> [--json]
```

## 2.4 search
Search for text patterns (regex supported).
```bash
claw pdf search <SRC_PDF> --term <PATTERN> [--json]
```

## 2.5 ocr
Optical Character Recognition for scanned documents.
```bash
claw pdf ocr <SRC_PDF> -o <OUT_PDF> [--lang eng] [--force]
```

## 2.6 chars
Extract individual character positions and properties.
```bash
claw pdf chars <SRC_PDF> [--json]
```

## 2.7 words
Extract words with font attributes; filter by name/size/style.
```bash
claw pdf words <SRC_PDF> [--pages N-M] [--filter "fontname~=Bold"] [-o out.json] [--json]
```

## 2.8 shapes
Dump vector shapes (lines, rects, curves) from the page content stream.
```bash
claw pdf shapes <SRC_PDF> [--pages N-M] [--kind line|rect|curve|all] [-o out.json] [--json]
```

## 2.9 extract-images
Save embedded raster images to a directory; filter by dimensions/format.
```bash
claw pdf extract-images <SRC_PDF> --out <DIR> [--pages N-M] [--format png|jpeg|original] [--min-width N] [--min-height N]
```

---

## 3.1 merge
Combine multiple PDF files into one.
```bash
claw pdf merge <INPUTS...> -o <OUT_PDF> [--force]
```

## 3.2 split
Split a PDF by page ranges or into individual pages.
```bash
claw pdf split <SRC_PDF> --out-dir <DIR> [--per-page] [--ranges 1-5,6-10] [--force]
```

## 3.3 rotate
Rotate pages in increments of 90 degrees.
```bash
claw pdf rotate <SRC_PDF> --by <DEGREES> -o <OUT_PDF> [--force]
```

## 3.4 crop
Crop pages to a specific bounding box.
```bash
claw pdf crop <SRC_PDF> --box <x0,y0,x1,y1> -o <OUT_PDF> [--force]
```

## 3.5 render
Render PDF pages to images (PNG/JPG).
```bash
claw pdf render <SRC_PDF> --page <N> -o <OUT_IMAGE> [--dpi 300] [--force]
```

## 3.6 watermark
Apply a text or image watermark to all pages.
```bash
claw pdf watermark <SRC_PDF> --text <TEXT> -o <OUT_PDF> [--opacity 0.5] [--force]
```

## 3.7 redact
Black out text or areas and remove underlying data.
```bash
claw pdf redact <SRC_PDF> --regex <PATTERN> -o <OUT_PDF> [--force]
```

---

## 4.1 annotate
Add highlights, underlines, or sticky notes.
```bash
claw pdf annotate <SRC_PDF> --type highlight --range <TEXT> -o <OUT_PDF> [--force]
```

## 4.2 attach
Manage file attachments within the PDF.
```bash
claw pdf attach <SRC_PDF> --file <ATTACHMENT> -o <OUT_PDF> [--force]
```

## 4.3 bookmark
Manage the document outline (bookmarks).
```bash
claw pdf bookmark <list|add|remove> <SRC_PDF> [--title <TEXT>] [--page <N>]
```

## 4.4 form
List, fill, or flatten PDF form fields (AcroForms).
```bash
claw pdf form <list|fill> <SRC_PDF> [--data <FILE.json>] -o <OUT_PDF>
```

## 4.5 labels
Set or read page labels (e.g., i, ii, 1, 2).
```bash
claw pdf labels <SRC_PDF> [--json]
```

## 4.6 layer
List or toggle visibility of PDF layers (Optional Content Groups).
```bash
claw pdf layer <list|toggle> <SRC_PDF> [--name <LAYER>]
```

## 4.7 stamp
Apply a digital stamp to the document.
```bash
claw pdf stamp <SRC_PDF> --image <FILE.png> --page <N> -o <OUT_PDF> [--force]
```

## 4.8 tables-debug
Visualizes detected table boundaries for troubleshooting.
```bash
claw pdf tables-debug <SRC_PDF> -o <OUT_IMG>
```

## 4.9 toc
Extract or modify the Table of Contents.
```bash
claw pdf toc <SRC_PDF> [--json]
```

## 4.10 flatten
Bake AcroForm fields and/or annotations into the page content (irreversible).
```bash
claw pdf flatten <SRC_PDF> [--forms/--no-forms] [--annotations/--no-annotations] (-o <OUT> | --in-place) [--force]
```

## 4.11 journal
Stage edits in a sidecar; commit or rollback atomically (subcommands: `start`, `status`, `commit`, `rollback`).
```bash
claw pdf journal start <SRC_PDF>
claw pdf journal status <SRC_PDF>
claw pdf journal commit <SRC_PDF>
claw pdf journal rollback <SRC_PDF>
```

---

## 5.1 encrypt/decrypt
Manage PDF password protection and permissions.
```bash
claw pdf encrypt <SRC_PDF> --password <PW> -o <OUT_PDF> [--force]
claw pdf decrypt <SRC_PDF> --password <PW> -o <OUT_PDF> [--force]
```

---

## 6.1 meta
Read or write PDF core metadata (title, author, subject, keywords, ...).
```bash
claw pdf meta get <SRC_PDF> [--json]
claw pdf meta set <SRC_PDF> [--title <T>] [--author <A>] [--subject <S>] [--keywords <K>]
```

---

## Footguns
- **Invisible Text** — Some PDFs contain invisible text layers (OCR results) over images. `extract-text` will find them, but they may be poorly aligned.
- **Incremental Saves** — PDFs can be saved "incrementally," keeping old versions of data. `claw` performs a full rewrite to ensure deleted/redacted data is purged.

## Escape Hatch
Underlying libraries: `PyMuPDF` (fitz) for performance, `pdfplumber` for table extraction, and `pypdf` for structural merging.

## Quick Reference
| Task | Command |
|------|---------|
| Extract Text | `claw pdf extract-text doc.pdf` |
| Merge Files | `claw pdf merge *.pdf -o combined.pdf` |
| OCR Scan | `claw pdf ocr scan.pdf -o searchable.pdf` |
| Fill Form | `claw pdf form fill doc.pdf --data f.json -o out.pdf` |
| Redact Info | `claw pdf redact doc.pdf --regex "\d{3}-\d{2}-\d{4}"` |
