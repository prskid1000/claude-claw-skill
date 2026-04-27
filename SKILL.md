---
name: claude-claw
description: >
  Productivity OS index for spreadsheets, documents, PDFs, media, and automation.
---

# Claude Claw — Productivity OS

> All Python deps + the `claw` CLI live in a skill-local venv at `~/.claude/skills/claude-claw/.venv/`. 
> Use `claw` on PATH as the primary entry point.

- [Bootstrap](#bootstrap) · [Workflow](#workflow) · [Documentation Index](#documentation-index) · [Scripts](#scripts)

## Bootstrap

```bash
python ~/.claude/skills/claude-claw/scripts/healthcheck.py --install     # create .venv + install everything
```

## Workflow

`Source -> Transform (claw) -> Output (/tmp/) -> Deliver (gws)`

## Documentation Index

### 📊 Excel (.xlsx) — [Full Ref](references/claw/xlsx.md)
- [new](references/claw/xlsx.md#11-new) — Create blank workbook
- [from-csv](references/claw/xlsx.md#12-from-csv) — Multi-CSV to sheets
- [from-json](references/claw/xlsx.md#13-from-json) — JSON array import
- [from-html](references/claw/xlsx.md#14-from-html) — Scrape HTML tables
- [from-pdf](references/claw/xlsx.md#15-from-pdf) — PDF table extraction
- [read](references/claw/xlsx.md#21-read) — Cells to JSON/CSV
- [to-csv](references/claw/xlsx.md#22-to-csv) — Sheet to CSV
- [to-pdf](references/claw/xlsx.md#23-to-pdf) — Render via LibreOffice
- [sql](references/claw/xlsx.md#24-sql) — Query sheets (DuckDB)
- [stat](references/claw/xlsx.md#25-stat) — Column summary stats
- [append](references/claw/xlsx.md#31-append) — Add rows to sheet
- [richtext](references/claw/xlsx.md#32-richtext) — Per-run cell formatting
- [image](references/claw/xlsx.md#33-image) — Embed images in sheet
- [style](references/claw/xlsx.md#41-style) — Format font/fill/border
- [freeze](references/claw/xlsx.md#42-freeze) — Lock header panes
- [filter](references/claw/xlsx.md#43-filter) — Enable Excel auto-filter
- [conditional](references/claw/xlsx.md#44-conditional) — Cell-is/Formula rules
- [format](references/claw/xlsx.md#45-format) — Set number format
- [table](references/claw/xlsx.md#46-table) — Define structured tables
- [chart](references/claw/xlsx.md#47-chart) — Add Bar/Line/Pie
- [validate](references/claw/xlsx.md#51-validate) — Dropdowns & constraints
- [name](references/claw/xlsx.md#52-name) — Manage defined names
- [print-setup](references/claw/xlsx.md#53-print-setup) — Print area, fit-to-page, orientation
- [protect](references/claw/xlsx.md#61-protect) — Sheet/workbook password lock
- [meta](references/claw/xlsx.md#71-meta) — Workbook core properties
- [pivots](references/claw/xlsx.md#72-pivots) — Pivot-table read

### 📝 Word (.docx) — [Full Ref](references/claw/docx.md)
- [new](references/claw/docx.md#11-new) — Blank doc (optional template)
- [from-md](references/claw/docx.md#12-from-md) — Markdown → docx via pandoc
- [read](references/claw/docx.md#21-read) — Text/JSON/tables/outline
- [comments](references/claw/docx.md#22-comments) — Comment-review ops
- [diff](references/claw/docx.md#23-diff) — Tracked insert/delete dump
- [add-heading](references/claw/docx.md#31-add-heading) — Insert level 1–9
- [add-paragraph](references/claw/docx.md#32-add-paragraph) — Insert formatted text
- [add-table](references/claw/docx.md#33-add-table) — Insert CSV/JSON data
- [add-image](references/claw/docx.md#34-add-image) — Insert scaled image
- [insert](references/claw/docx.md#35-insert) — Pagebreaks & structural
- [hyperlink](references/claw/docx.md#36-hyperlink) — Insert/replace links
- [style](references/claw/docx.md#41-style) — Define / apply styles
- [section](references/claw/docx.md#42-section) — Section/page properties
- [header](references/claw/docx.md#43-header) — Set section header
- [footer](references/claw/docx.md#44-footer) — Set section footer
- [toc](references/claw/docx.md#45-toc) — Insert TOC field
- [table](references/claw/docx.md#46-table) — Table layout (autofit, widths)
- [meta](references/claw/docx.md#51-meta) — Core doc properties
- [custom-xml](references/claw/docx.md#52-custom-xml) — Custom XML parts on OPC

### 🎞 PowerPoint (.pptx) — [Full Ref](references/claw/pptx.md)
- [new](references/claw/pptx.md#11-new) — Blank deck (optional template)
- [add-slide](references/claw/pptx.md#12-add-slide) — Append slide
- [from-outline](references/claw/pptx.md#13-from-outline) — Markdown outline → deck
- [add-chart](references/claw/pptx.md#21-add-chart) — Bar/line/pie from CSV
- [add-table](references/claw/pptx.md#22-add-table) — Native table from data
- [add-image](references/claw/pptx.md#23-add-image) — Place picture
- [add-shape](references/claw/pptx.md#24-add-shape) — Rect/oval/arrow/callout
- [fill](references/claw/pptx.md#25-fill) — Write text into placeholder
- [brand](references/claw/pptx.md#31-brand) — Apply logo/colors/fonts
- [chart](references/claw/pptx.md#32-chart) — Re-read CSV → refresh chart data
- [notes](references/claw/pptx.md#33-notes) — Speaker-notes get/set
- [reorder](references/claw/pptx.md#34-reorder) — Reorder slides
- [image](references/claw/pptx.md#35-image) — Picture-shape crop
- [link](references/claw/pptx.md#36-link) — Hyperlink on shape
- [meta](references/claw/pptx.md#41-meta) — Core deck properties

### 📄 PDF — [Full Ref](references/claw/pdf.md)
- [from-html](references/claw/pdf.md#11-from-html) — HTML → PDF (PyMuPDF Story)
- [from-md](references/claw/pdf.md#12-from-md) — Markdown → PDF
- [qr](references/claw/pdf.md#13-qr) — QR code PDF
- [barcode](references/claw/pdf.md#14-barcode) — Barcode PDF
- [convert](references/claw/pdf.md#15-convert) — EPUB/XPS/CBZ → PDF
- [extract-text](references/claw/pdf.md#21-extract-text) — Plain/JSON text
- [extract-tables](references/claw/pdf.md#22-extract-tables) — Tabular extraction
- [info](references/claw/pdf.md#23-info) — Metadata + structural summary
- [search](references/claw/pdf.md#24-search) — Term + bbox + context
- [ocr](references/claw/pdf.md#25-ocr) — Add OCR text layer
- [chars](references/claw/pdf.md#26-chars) — Per-char positional dump
- [words](references/claw/pdf.md#27-words) — Words with font attributes
- [shapes](references/claw/pdf.md#28-shapes) — Vector lines/rects/curves
- [extract-images](references/claw/pdf.md#29-extract-images) — Save embedded rasters
- [merge](references/claw/pdf.md#31-merge) — Join multiple PDFs
- [split](references/claw/pdf.md#32-split) — Explode into ranges/pages
- [rotate](references/claw/pdf.md#33-rotate) — Rotate pages
- [crop](references/claw/pdf.md#34-crop) — Crop pages to box
- [render](references/claw/pdf.md#35-render) — Page → PNG/JPG
- [watermark](references/claw/pdf.md#36-watermark) — Stamp text across pages
- [redact](references/claw/pdf.md#37-redact) — Sanitize text + pixels
- [annotate](references/claw/pdf.md#41-annotate) — Add highlights / notes / ink
- [attach](references/claw/pdf.md#42-attach) — Embedded file attachments
- [bookmark](references/claw/pdf.md#43-bookmark) — Outline operations
- [form](references/claw/pdf.md#44-form) — AcroForm list/fill
- [labels](references/claw/pdf.md#45-labels) — Page-label operations
- [layer](references/claw/pdf.md#46-layer) — OCG (optional content)
- [stamp](references/claw/pdf.md#47-stamp) — Image stamp
- [tables-debug](references/claw/pdf.md#48-tables-debug) — Visualize detection edges
- [toc](references/claw/pdf.md#49-toc) — Read/write outline
- [flatten](references/claw/pdf.md#410-flatten) — Bake forms/annotations
- [journal](references/claw/pdf.md#411-journal) — Atomic edit sessions
- [encrypt/decrypt](references/claw/pdf.md#51-encryptdecrypt) — Password protection
- [meta](references/claw/pdf.md#61-meta) — Core metadata get/set

### 🖼 Images — [Full Ref](references/claw/img.md)
- [resize](references/claw/img.md#11-resize) — Scale via geometry
- [fit](references/claw/img.md#12-fit) — Scale + crop to exact dims
- [pad](references/claw/img.md#13-pad) — Letterbox to size
- [thumb](references/claw/img.md#14-thumb) — Fast thumbnail
- [crop](references/claw/img.md#15-crop) — Pixel box crop
- [convert](references/claw/img.md#21-convert) — Format encode (auto by ext)
- [to-jpeg](references/claw/img.md#22-to-jpeg) — Encode JPEG, flatten alpha
- [to-webp](references/claw/img.md#23-to-webp) — Encode WebP
- [watermark](references/claw/img.md#31-watermark) — Text/logo at corner
- [enhance](references/claw/img.md#32-enhance) — Tonal corrections
- [sharpen](references/claw/img.md#33-sharpen) — Unsharp mask
- [composite](references/claw/img.md#34-composite) — Alpha-composite layers
- [overlay](references/claw/img.md#35-overlay) — Logo at named corner
- [exif](references/claw/img.md#41-exif) — Read/strip/auto-rotate EXIF
- [rename](references/claw/img.md#51-rename) — EXIF-templated rename
- [batch](references/claw/img.md#52-batch) — Op chain over directory
- [gif-from-frames](references/claw/img.md#53-gif-from-frames) — Animated GIF builder

### 🎬 Media (audio/video) — [Full Ref](references/claw/media.md)
- [info](references/claw/media.md#11-info) — FFprobe stream dump
- [extract-audio](references/claw/media.md#21-extract-audio) — Video → MP3/WAV
- [thumbnail](references/claw/media.md#22-thumbnail) — Frame / contact sheet
- [trim](references/claw/media.md#31-trim) — Cut [t_from, t_to]
- [compress](references/claw/media.md#32-compress) — 2-pass target-size or CRF
- [scale](references/claw/media.md#33-scale) — Resize video geometry
- [speed](references/claw/media.md#34-speed) — Change playback factor
- [fade](references/claw/media.md#35-fade) — Fade in/out video+audio
- [burn-subs](references/claw/media.md#36-burn-subs) — Hardcode SRT
- [concat](references/claw/media.md#37-concat) — Join clips
- [crop-auto](references/claw/media.md#38-crop-auto) — Detect+remove letterbox
- [loudnorm](references/claw/media.md#39-loudnorm) — EBU R128 two-pass
- [gif](references/claw/media.md#310-gif) — Slice → animated GIF

### ☁️ Google Drive — [Full Ref](references/claw/drive.md)
- [upload](references/claw/drive.md#11-upload) — Upload local file (auto-converts office formats)
- [copy](references/claw/drive.md#12-copy) — Duplicate a Drive file
- [download](references/claw/drive.md#21-download) — Fetch any file (binary blobs as-is; Google-native via `--as pdf|xlsx|docx|md|...`)
- [list](references/claw/drive.md#22-list) — Query Drive files
- [info](references/claw/drive.md#23-info) — File metadata (name/mime/size/parents/owners)
- [move](references/claw/drive.md#31-move) — Move file between folders
- [rename](references/claw/drive.md#32-rename) — Rename Drive file
- [delete](references/claw/drive.md#33-delete) — Trash (default) or `--permanent` to skip Trash
- [share](references/claw/drive.md#41-share) — Grant access (user/domain/anyone)
- [share-list](references/claw/drive.md#42-share-list) — List permissions
- [share-revoke](references/claw/drive.md#43-share-revoke) — Remove user access

### 📃 Google Docs — [Full Ref](references/claw/doc.md)
- [create](references/claw/doc.md#11-create) — New blank Doc
- [read](references/claw/doc.md#12-read) — Text or full JSON structure
- [append](references/claw/doc.md#21-append) — Append markdown/text
- [build](references/claw/doc.md#22-build) — Apply markdown file (replace)
- [replace](references/claw/doc.md#23-replace) — Find-and-replace literal text
- [export](references/claw/doc.md#31-export) — DOC_ID → pdf/docx/html/md/txt/epub
- [tabs](references/claw/doc.md#32-tabs) — Tab list/operations

### ✉️ Email (Gmail) — [Full Ref](references/claw/email.md)
- [send](references/claw/email.md#11-send) — Compose + send via Gmail API
- [draft](references/claw/email.md#12-draft) — Create a Gmail draft
- [reply](references/claw/email.md#21-reply) — Reply preserving thread
- [forward](references/claw/email.md#22-forward) — Forward with optional note
- [search](references/claw/email.md#31-search) — Gmail query syntax search
- [download-attachment](references/claw/email.md#32-download-attachment) — Save attachment locally

### 🌐 Web — [Full Ref](references/claw/web.md)
- [fetch](references/claw/web.md#11-fetch) — HTTP GET/POST with retry
- [snapshot](references/claw/web.md#12-snapshot) — Inline CSS/img/font as data: URLs
- [extract](references/claw/web.md#21-extract) — Main-article text (trafilatura)
- [links](references/claw/web.md#22-links) — Enumerate `<a href>`
- [table](references/claw/web.md#23-table) — Pull `<table>` → CSV/JSON

### 🧹 HTML — [Full Ref](references/claw/html.md)
- [select](references/claw/html.md#11-select) — CSS or XPath query
- [text](references/claw/html.md#12-text) — Flattened text extraction
- [strip](references/claw/html.md#21-strip) — Decompose matched elements
- [unwrap](references/claw/html.md#22-unwrap) — Drop tag, keep children
- [wrap](references/claw/html.md#23-wrap) — Wrap matches in new parent
- [replace](references/claw/html.md#24-replace) — `tag.replace_with(...)`
- [sanitize](references/claw/html.md#31-sanitize) — Allow-list cleaning
- [absolutize](references/claw/html.md#32-absolutize) — Relative → absolute URLs
- [rewrite](references/claw/html.md#33-rewrite) — Substring rewrite over link attrs
- [fmt](references/claw/html.md#34-fmt) — Pretty-print HTML
- [diagnose](references/claw/html.md#35-diagnose) — Show parser-by-parser results

### 📐 XML — [Full Ref](references/claw/xml.md)
- [xpath](references/claw/xml.md#11-xpath) — XPath 1.0 query
- [stream-xpath](references/claw/xml.md#12-stream-xpath) — Stream giant XML by tag
- [to-json](references/claw/xml.md#13-to-json) — XML → JSON
- [xslt](references/claw/xml.md#21-xslt) — XSLT 1.0 transform
- [fmt](references/claw/xml.md#22-fmt) — Pretty-print XML
- [canonicalize](references/claw/xml.md#23-canonicalize) — Emit canonical XML
- [validate](references/claw/xml.md#31-validate) — Schema validate (XSD/RNG/DTD)

### 🔄 Conversion — [Full Ref](references/claw/convert.md)
- [convert](references/claw/convert.md#11-convert) — Pandoc src → dst
- [list-formats](references/claw/convert.md#12-list-formats) — Pandoc input/output formats
- [md2pdf-nolatex](references/claw/convert.md#21-md2pdf-nolatex) — Markdown → PDF without LaTeX
- [slides](references/claw/convert.md#22-slides) — Markdown slides → reveal/Beamer/PPTX
- [book](references/claw/convert.md#23-book) — Concat chapters → single doc

### 🌍 Browser — [Full Ref](references/claw/browser.md)
- [launch](references/claw/browser.md#11-launch) — Chrome/Edge with --remote-debugging-port
- [stop](references/claw/browser.md#12-stop) — Terminate debug processes
- [verify](references/claw/browser.md#21-verify) — Check debug port is responding

### 🪛 Pipeline — [Full Ref](references/claw/pipeline.md)
- [run](references/claw/pipeline.md#11-run) — Execute YAML DAG (`--resume` for restart)
- [validate](references/claw/pipeline.md#21-validate) — Static recipe check
- [graph](references/claw/pipeline.md#22-graph) — Mermaid/DOT visualization
- [list-steps](references/claw/pipeline.md#23-list-steps) — Enumerate step types

### 🩺 Diagnostics
- `claw doctor` — [Full Ref](references/claw/doctor.md) — Verify external deps + auth (`--scope all|packages|cli|gws`)
- `claw completion` — [Full Ref](references/claw/completion.md) — Emit shell completion (bash/zsh/fish/pwsh)

---

## Scripts

- [scripts/claw/](scripts/claw/) — The core `claw` CLI package.
- [scripts/healthcheck.py](scripts/healthcheck.py) — Environment verification and install.
- [scripts/patchers/](scripts/patchers/) — System/binary patchers.
- [scripts/wrappers/](scripts/wrappers/) — Insiders/local-model launchers.
