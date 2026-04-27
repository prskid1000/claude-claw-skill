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
Convert HTML to PDF via PyMuPDF Story. Remote `<link>` stylesheets are skipped unless `--fetch-remote-css`.
```bash
claw pdf from-html <SRC_HTML> <OUT_PDF> [--page-size Letter|Legal|A4|A3] [--rect x0,y0,x1,y1] [--css FILE] [--fetch-remote-css]
```

## 1.2 from-md
Convert Markdown to PDF. `--engine` picks the renderer (`reportlab` default).
```bash
claw pdf from-md <SRC_MD> <OUT_PDF> [--theme minimal|corporate|academic|dark] [--page-size Letter|A4|Legal] [--margin M] [--toc] [--title T] [--author A] [--engine reportlab|pymupdf|pandoc]
```

## 1.3 qr
Generate a single-page PDF containing a QR code. `--size` is in points.
```bash
claw pdf qr --value <TEXT> -o <OUT_PDF> [--size POINTS] [--ec L|M|Q|H] [--page-size Letter|A4|Legal] [--caption TEXT]
```

## 1.4 barcode
Generate a single-page barcode PDF.
```bash
claw pdf barcode --type code128|ean|ean13|upc|upca|qr --value <TEXT> -o <OUT_PDF> [--size WxH[unit]] [--caption TEXT]
```

## 1.5 convert
Convert EPUB / XPS / CBZ / FB2 / OXPS into PDF via PyMuPDF.
```bash
claw pdf convert <SRC> <OUT_PDF> [--page-size A4]
```

---

## 2.1 extract-text
Extract text from the PDF in one of PyMuPDF's output modes.
```bash
claw pdf extract-text <SRC_PDF> [--pages N-M] [--mode plain|blocks|dict|html|xhtml|xml|json] [-o OUT|-] [--dehyphenate] [--preserve-ligatures] [--json]
```

## 2.2 extract-tables
Detect and extract tabular data via pdfplumber strategies. Output format follows `-o`'s extension (`.csv` / `.json` / `.xlsx`); stdout CSV if omitted.
```bash
claw pdf extract-tables <SRC_PDF> [--pages N-M] [--strategy lines|lines_strict|text|explicit] [--vlines x1,x2,...] [--hlines y1,y2,...] [--bbox x0,y0,x1,y1] [-o OUT] [--json]
```

## 2.3 info
Display metadata, encryption status, and page count.
```bash
claw pdf info <SRC_PDF> [--json]
```

## 2.4 search
Search the PDF; returns page + bbox + surrounding context for each hit.
```bash
claw pdf search <SRC_PDF> --term <PATTERN> [--regex] [--case-sensitive] [--pages N-M] [--context N] [--json]
```

## 2.5 ocr
Add an OCR text layer over scanned pages (requires `tesseract` on PATH).
```bash
claw pdf ocr <SRC_PDF> [--lang eng+fra] [--dpi N] [--pages N-M] [--sidecar] [--tessdata DIR] (-o <OUT_PDF> | --in-place)
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
Combine multiple PDFs into one. Each input may carry an inline range, e.g. `file.pdf:1-3,7`. `--toc-from filenames` adds a top-level outline entry per input.
```bash
claw pdf merge <INPUTS...> -o <OUT_PDF> [--toc-from filenames|none]
```

## 3.2 split
Split a PDF by ranges or into individual pages. `--name-template` supports `{stem} {n} {start} {end}`.
```bash
claw pdf split <SRC_PDF> --out-dir <DIR> (--ranges 1-5,6-end | --per-page) [--name-template "{stem}_{n}"]
```

## 3.3 rotate
Rotate pages in increments of 90 degrees. `--by` must be `90|-90|180|270`.
```bash
claw pdf rotate <SRC_PDF> --by <90|-90|180|270> [--pages N-M] (-o <OUT_PDF> | --in-place)
```

## 3.4 crop
Crop pages to a specific bounding box. `--box-type` selects which page box to modify.
```bash
claw pdf crop <SRC_PDF> --box <x0,y0,x1,y1> [--pages N-M] [--box-type media|crop|trim|bleed|art] (-o <OUT_PDF> | --in-place)
```

## 3.5 render
Render a PDF page to a raster image (PNG/JPG). `--clip` is in PDF points with top-left origin.
```bash
claw pdf render <SRC_PDF> --page <N> -o <OUT_IMAGE> [--dpi 300 | --zoom 2.0] [--colorspace rgb|gray|cmyk] [--clip x0,y0,x1,y1] [--no-annots]
```

## 3.6 watermark
Apply a text watermark across pages. `--layer behind` places it under content.
```bash
claw pdf watermark <SRC_PDF> --text <TEXT> [--opacity 0.5] [--rotate DEG] [--color C] [--font F] [--size N] [--pages N-M] [--layer behind|above] (-o <OUT_PDF> | --in-place)
```

## 3.7 redact
Black out text or areas and purge underlying data. Supply at least one of `--regex`, `--terms`, or `--boxes`. `--preview` renders a PNG without applying.
```bash
claw pdf redact <SRC_PDF> [--regex PATTERN] [--terms FILE] [--boxes FILE.json] [--fill COLOR] [--pages N-M] [--preview PNG] (-o <OUT_PDF> | --in-place)
```

---

## 4.1 annotate
Add highlights, sticky notes, or free-hand ink to a single page. Supply one of `--highlight`, `--note --at`, or `--ink-path`.
```bash
claw pdf annotate <SRC_PDF> --page <N> [--highlight TERM [--regex]] [--note TEXT --at x,y] [--ink-path "x1,y1 x2,y2 ..."] [--color C] [--opacity F] [--author A] (-o <OUT_PDF> | --in-place)
```

## 4.2 attach
Manage embedded file attachments. Subcommand group: `add | list | extract | remove`.
```bash
claw pdf attach add     <SRC_PDF> --file <ATTACHMENT> [--name N] [--description D] (-o <OUT> | --in-place)
claw pdf attach list    <SRC_PDF> [--json]
claw pdf attach extract <SRC_PDF> --name <ATTACHMENT_NAME> -o <OUT_FILE>
claw pdf attach remove  <SRC_PDF> --name <ATTACHMENT_NAME> (-o <OUT> | --in-place)
```

## 4.3 bookmark
Append a bookmark to the document outline. Only `add` is implemented; for full TOC editing use `pdf toc set`.
```bash
claw pdf bookmark add <SRC_PDF> --title <TEXT> --page <N> [--level N] [--parent "Parent Title"] (-o <OUT> | --in-place)
```

## 4.4 form
AcroForm operations. `fill` reads a JSON object mapping field name → value from `--values`; `--flatten` bakes filled values into page content.
```bash
claw pdf form list <SRC_PDF> [--json]
claw pdf form fill <SRC_PDF> --values <FILE.json> [--flatten] (-o <OUT_PDF> | --in-place)
```

## 4.5 labels
Set page labels via a `--rule` like `"i:1-5,1:6-end"`. Styles: `i I a A 1`.
```bash
claw pdf labels set <SRC_PDF> --rule "i:1-5,1:6-end" (-o <OUT_PDF> | --in-place)
```

## 4.6 layer
Toggle visibility of an OCG (Optional Content Group) by name. Only `toggle` is implemented.
```bash
claw pdf layer toggle <SRC_PDF> --name <LAYER> [--show | --hide] (-o <OUT_PDF> | --in-place)
```

## 4.7 stamp
Stamp an image onto pages. Position via `--at` anchor (TL/TR/BL/BR/C) plus `--offset`.
```bash
claw pdf stamp <SRC_PDF> --image <FILE.png> [--scale 0..1] [--at TL|TR|BL|BR|C] [--offset x,y] [--opacity F] [--pages N-M] (-o <OUT_PDF> | --in-place)
```

## 4.8 tables-debug
Render a page with pdfplumber's detected table edges drawn on top.
```bash
claw pdf tables-debug <SRC_PDF> --page <N> -o <OUT.png> [--strategy lines|lines_strict|text|explicit] [--vlines x1,x2,...] [--hlines y1,y2,...] [--resolution DPI]
```

## 4.9 toc
Read / overwrite the table of contents (outline). `set --json` takes a JSON array matching `doc.set_toc()`.
```bash
claw pdf toc get <SRC_PDF> [--json]
claw pdf toc set <SRC_PDF> --json <FILE.json> (-o <OUT_PDF> | --in-place)
```

## 4.10 flatten
Bake AcroForm fields and/or annotations into the page content (irreversible).
```bash
claw pdf flatten <SRC_PDF> [--forms/--no-forms] [--annotations/--no-annotations] (-o <OUT> | --in-place)
```

## 4.11 journal
Stage edits in a sidecar; commit or rollback atomically. All subcommands take `--name <SESSION>`; `start` binds the session to a `<SRC_PDF>`.
```bash
claw pdf journal start    <SRC_PDF> --name <SESSION>
claw pdf journal status   --name <SESSION> [--json]
claw pdf journal commit   --name <SESSION> (-o <OUT_PDF> | --in-place)
claw pdf journal rollback --name <SESSION>
```

---

## 5.1 encrypt/decrypt
Manage PDF password protection and permissions. Cipher flags are mutually exclusive (`--aes256` needs `pycryptodome`). `--allow` / `--deny` accept CSV subsets of `print,copy,modify,annotate,fill-forms,assemble,print-high`.
```bash
claw pdf encrypt <SRC_PDF> -p <PW> [--owner-password <PW>] [--aes256|--aes128|--rc4-128] [--allow csv] [--deny csv] -o <OUT_PDF>
claw pdf decrypt <SRC_PDF> -p <PW> (-o <OUT_PDF> | --in-place)
```

---

## 6.1 meta
Read or write PDF core metadata. `--keywords` is comma-separated; dates use `YYYY-MM-DD`.
```bash
claw pdf meta get <SRC_PDF> [--json]
claw pdf meta set <SRC_PDF> [--title T] [--author A] [--subject S] [--keywords K1,K2] [--creator C] [--producer P] [--creation-date YYYY-MM-DD] [--mod-date YYYY-MM-DD] (-o <OUT_PDF> | --in-place)
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
| Fill Form | `claw pdf form fill doc.pdf --values f.json -o out.pdf` |
| Redact Info | `claw pdf redact doc.pdf --regex "\d{3}-\d{2}-\d{4}"` |
