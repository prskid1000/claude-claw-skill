---
name: claude-claw
description: >
  Reference guide for documents, spreadsheets, presentations, PDFs, images, video, audio,
  Google Workspace, ClickUp, MySQL, and media processing.
---

# Claude Claw — Productivity OS

- [Bootstrap](#bootstrap) · [Workflow](#workflow) · [Templates](#templates) · [Scripts](#scripts)

## Bootstrap

```bash
python ~/.claude/skills/claude-claw/scripts/healthcheck.py
```

## Workflow

`Source -> Transform (Python) -> Output (/tmp/) -> Deliver (gws)`

## Decision-Tree List Format

Every index / TOC in this skill (the File Map below, plus each reference's and example's Contents list) uses the same decision-tree shape. Apply it to any markdown file that indexes capability by user task.

- Top level: `- **VERB …**` — the *user's intent* in bold caps (CREATE, READ, EDIT, CONVERT, PATCH, SEND, QUERY, …). New tools go under an existing verb when possible; add a new verb only for a genuinely new task category.
- Second level: one option per line, ` — ` separator before the backticked package/binary.
- Third level — choose one shape per node, don't mix:
  - **Expanded** — `- Ref:` + `- Ex:` sub-bullets, one anchor per line (use for options with many subsections).
  - **Compact** — a single line of `·`-separated anchor links (use for dense sub-capabilities where a full nested list would dominate the page).
- Anchors: lowercase kebab-case, strip punctuation, spaces → hyphens. Link labels restate section purpose in 3–8 words — don't just repeat the heading.
- Never force the tree onto code blocks, tables, or API detail — only onto index lists.
- Broken anchors silently degrade retrieval; treat them as build-breaks.

Copy [references/_TEMPLATE.md](references/_TEMPLATE.md) or [examples/_TEMPLATE.md](examples/_TEMPLATE.md) for a pre-filled shape. For adding or improving `claw` commands, follow the agent checklist in [references/claw/contributing.md](references/claw/contributing.md).

## File Map

Primary entry point: the **`claw`** CLI. Library-level references are escape hatches — use when `claw` doesn't expose what you need. See [references/claw/README.md](references/claw/README.md) for install, global flags, help UX, exit codes, and plugin model.

- **CREATE a document**
  - Excel (.xlsx) — `claw xlsx`
    - Ref: [claw xlsx](references/claw/xlsx.md) — `new`, `from-csv`, `from-json`, `from-html`, `from-pdf`, `append`, `style`, `chart`, `table`, `validate`, `protect`, `richtext`, `freeze`, `filter`, `conditional`, `meta`
    - Escape hatch: [openpyxl API](references/document-creation.md#11-workbook--worksheet-operations) — custom chart construction, overlapping conditional-formatting rule stacks, VBA preservation, pivot-table read, worksheet-scoped styles
    - Ex: [recipes — xlsx](examples/claw-recipes.md)
  - Word (.docx) — `claw docx`
    - Ref: [claw docx](references/claw/docx.md) — `new`, `from-md`, `add-heading|paragraph|table|image`, `header`, `footer`, `toc`, `style`, `section`, `comments`, `custom-xml`
    - Escape hatch: [python-docx API](references/document-creation.md#21-document-operations) — SmartArt, embedded Excel/chart objects, numbering.xml, track-changes write
    - Ex: [recipes — docx](examples/claw-recipes.md)
  - PowerPoint (.pptx) — `claw pptx`
    - Ref: [claw pptx](references/claw/pptx.md) — `new`, `add-slide`, `add-chart`, `add-table`, `add-image`, `brand`, `chart refresh`, `notes`, `reorder`
    - Escape hatch: [python-pptx API](references/document-creation.md#31-presentation--slides) — KPI dashboards, animations, SmartArt, master-slide construction
    - Ex: [recipes — pptx](examples/claw-recipes.md)
  - PDF from scratch — `claw pdf from-html|from-md|qr|barcode`
    - Ref: [claw pdf § CREATE](references/claw/pdf.md)
    - Escape hatch: [reportlab API](references/pdf-tools.md#4-reportlab----pdf-generation) — freeform Canvas drawing, custom NumberedCanvas, AcroForm authoring, custom Flowables
  - Google Doc — `claw doc`
    - Ref: [claw doc](references/claw/doc.md) — `create`, `build` (markdown → chunked batchUpdate), `read`, `export`
    - Escape hatch: [gws docs commands](references/gws-cli.md#docs)
  - Google Sheet / Drive upload — `claw sheet`
    - Ref: [claw sheet](references/claw/sheet.md) — `upload --convert`, `download`, `share`, `list`, `move`, `copy`, `rename`, `delete`
    - Escape hatch: [gws sheets / drive commands](references/gws-cli.md#sheets)

- **READ / EXTRACT**
  - PDF → text — `claw pdf extract-text [--mode plain|blocks|dict|html]`
    - Ref: [claw pdf § READ](references/claw/pdf.md) · [OCR](references/claw/pdf.md)
    - Escape hatch: [PyMuPDF API](references/pdf-tools.md#1-pymupdf-fitz----pdf-read--edit--render)
  - PDF → tables — `claw pdf extract-tables [--strategy text --vlines …]`
    - Ref: [claw pdf § extract-tables](references/claw/pdf.md)
    - Escape hatch: [pdfplumber API](references/pdf-tools.md#3-pdfplumber----pdf-data-extraction)
  - PDF → images — `claw pdf extract-images | render`
    - Escape hatch: [PyMuPDF render API](references/pdf-tools.md#1-pymupdf-fitz----pdf-read--edit--render)
  - Excel → data — `claw xlsx read | sql | stat | to-csv`
  - HTML — `claw html select | text | strip | sanitize | absolutize | rewrite`
    - Ref: [claw html](references/claw/html.md)
    - Escape hatch: [BeautifulSoup4 reference](references/web-parsing.md#beautifulsoup4)
  - XML — `claw xml xpath | xslt | validate | canonicalize | stream-xpath | to-json`
    - Ref: [claw xml](references/claw/xml.md)
    - Escape hatch: [lxml reference](references/web-parsing.md#lxml) — XSLT params, Schematron, custom element classes, resolver registration
  - Web page → article — `claw web fetch | extract | table | links | snapshot`
    - Ref: [claw web](references/claw/web.md)
  - Email — `claw email search | download-attachment`

- **EDIT**
  - PDF annotate / redact / watermark — `claw pdf annotate|redact|watermark|stamp|flatten`
    - Ref: [claw pdf § STAMP / SECURE / ANNOTATE](references/claw/pdf.md)
    - Escape hatch: [PyMuPDF annotation API](references/pdf-tools.md#1-pymupdf-fitz----pdf-read--edit--render)
  - PDF merge / split / rotate / crop — `claw pdf merge|split|rotate|crop`
    - Escape hatch: [pypdf API](references/pdf-tools.md#2-pypdf2----pdf-merge--split--transform)
  - Excel / Word / PPT — same `claw xlsx|docx|pptx` nouns (CREATE verbs also edit in place)
  - Image — `claw img crop | resize | composite | exif | rename | batch`
    - Ref: [claw img](references/claw/img.md)
  - HTML tree — `claw html unwrap | wrap | replace`
  - XML — `claw xml fmt` (pretty-print) · [canonicalize](references/claw/xml.md)

- **CONVERT format** — `claw convert`
  - Any ↔ Any (Markdown, Word, PDF, HTML, EPUB, Slides, LaTeX, …) — `claw convert <in> <out> [--toc --template F --ref-doc F --css F --engine xelatex|weasyprint|typst]`
    - Ref: [claw convert](references/claw/convert.md)
    - Escape hatch: [Pandoc reference](references/conversion-tools.md) — custom Lua filters, Defaults YAML beyond passthrough
    - Ex: [recipes — convert](examples/claw-recipes.md)
  - PDF without LaTeX — `claw convert md2pdf-nolatex` (pandoc → HTML → PyMuPDF Story)
  - Multi-chapter book — `claw convert book <chapters…> [--csl FILE --bib FILE]`
  - Slides — `claw convert slides <in.md> --format reveal|beamer|pptx`

- **SEND / COMPOSE email** — `claw email`
  - Build + send — `claw email send --to … [--attach @PATH] [--html FILE] [--inline CID=…]`
    - Ref: [claw email](references/claw/email.md)
    - Escape hatch: [Python MIME + Gmail API reference](references/email-reference.md) — bulk merge >100 recipients, iCalendar, S/MIME
  - Reply / forward / draft — `claw email reply|forward|draft <msg-id>` (auto In-Reply-To / References)
  - Search — `claw email search --q "…" [--max N]`
  - Download attachment — `claw email download-attachment <msg-id> <att-id> --out PATH`

- **PROCESS images** — `claw img`
  - Resize / fit / pad / thumb / crop — `claw img resize|fit|pad|thumb|crop` (ImageMagick geometry syntax)
  - Enhance — `claw img enhance [--autocontrast --equalize --posterize --solarize]` · `sharpen` · `composite` · `watermark` · `overlay`
  - Convert format — `claw img convert | to-jpeg | to-webp [--animated --lossless]`
  - EXIF — `claw img exif [strip|auto-rotate|set]` · `rename --template "{CreateDate:%Y%m%d}_{Camera}.{ext}"`
  - Batch — `claw img batch <dir> --op "resize:1024|strip|webp:85" [--recursive]`
  - Frames → GIF — `claw img gif-from-frames <dir> --fps N`
    - Ref: [claw img](references/claw/img.md) · Escape hatch: [Pillow / ImageMagick reference](references/media-tools.md)

- **PROCESS video / audio** — `claw media`
  - Trim / compress / scale / concat — `claw media trim|compress|scale|concat`
  - Extract audio / frames — `claw media extract-audio|thumbnail|gif`
  - Normalize / effects — `claw media loudnorm|speed|fade|burn-subs|crop-auto`
  - Info — `claw media info <file> [--json]` (jc-style normalized ffprobe output)
    - Ref: [claw media](references/claw/media.md) · Escape hatch: [ffmpeg reference](references/media-tools.md#3-ffmpeg)

- **GOOGLE WORKSPACE** — `claw doc | claw sheet | claw email` (plus raw `gws` for uncovered APIs)
  - Docs — see CREATE / READ branches above
  - Sheets / Drive — see CREATE branch above
  - Gmail — see SEND branch above
  - Escape hatch (all services): [gws CLI reference](references/gws-cli.md) — Drive permissions, Calendar events, Tasks, batch-update request shapes

- **MANAGE tasks (ClickUp)** — `clickup` CLI (already a CLI — `claw` does not wrap)
  - Ref: [clickup-cli reference](references/clickup-cli.md)
  - Ex: [clickup-workflows.md](examples/clickup-workflows.md)

- **AUTOMATE browser** — `claw browser launch` + Chrome DevTools MCP
  - Launch — `claw browser launch [--profile default|throwaway] [--port 9222]`
    - Ref: [claw browser](references/claw/browser.md)
  - Post-launch automation — Chrome DevTools MCP tool calls
    - Ref: [chrome-devtools.md](references/chrome-devtools.md) · Ex: [chrome-devtools.md examples](examples/chrome-devtools.md)

- **QUERY database** — MySQL MCP
  - Ref: [MCP server setup](references/setup.md#4-mcp-servers)

- **ORCHESTRATE (multi-step pipelines)** — `claw pipeline run <recipe.yaml>`
  - Ref: [claw pipeline](references/claw/pipeline.md) — YAML DSL with `${vars.*}`, `${step.output}`, `${env:…}`, `${file:…}` interpolation; Nextflow-style content-hash cache + `--resume`; parallel execution; `retries`, `on-error`, `when:` guards
  - Commands: `run` · `validate` · `list-steps` · `graph`
  - Ex: [claw-pipelines.md](examples/claw-pipelines.md) — 10+ worked recipes (DB→XLSX+PDF→Drive→Gmail, CSV→Sheet, PDF tables→multi-sheet XLSX+summary, photo batch, video pipeline, book build)

- **DIAGNOSE environment** — `claw doctor`
  - Ref: [claw doctor](references/claw/doctor.md) — Python packages, CLI tools, LaTeX packages, Gmail scopes, config validation, cache health
  - Output modes: human · `--json` · `--prometheus`

- **SHELL COMPLETIONS** — `claw completion bash|zsh|fish|pwsh`
  - Ref: [claw completion](references/claw/completion.md)

- **SETUP / INSTALL**
  - [Python packages](references/setup.md#1-python-packages) · [CLI tools](references/setup.md#2-cli-tools) · [Google Workspace auth](references/setup.md#3-google-workspace-gws-auth) · [MCP servers](references/setup.md#4-mcp-servers) · [LSP plugins](references/setup.md#5-lsp-plugins) · [CLAUDE.md integration](references/setup.md#claudemd-integration) · [Notes](references/setup.md#6-notes)
  - [Run healthcheck (verify + auto-fix everything)](scripts/healthcheck.py)

- **CUSTOMIZE Claude apps (Code + Desktop) for local-model use**
  - [Overview & comparison table](references/claude-customization.md#at-a-glance) · [Why two different approaches](references/claude-customization.md#why-two-different-approaches) · [Launch wrappers (codel/claudel/claudedl/codexl)](references/claude-customization.md#launch-wrappers) · [Installing wrappers to PATH](references/claude-customization.md#installing-the-wrappers) · [When to use what](references/claude-customization.md#when-to-use-what)
  - **PATCH Claude Code binary** — bigger context/output ([detail](references/patchers/claude-patcher.md))
    - [Patchable constants](references/patchers/claude-patcher.md#patchable-constants) · [Usage](references/patchers/claude-patcher.md#usage) · [After updates](references/patchers/claude-patcher.md#after-claude-code-updates) · [How it works](references/patchers/claude-patcher.md#how-it-works)
  - **TOGGLE Claude Desktop Custom 3P (BYOM)** — registry policy, no binary changes ([detail](references/patchers/claude-desktop-3p.md))
    - [Requirements](references/patchers/claude-desktop-3p.md#requirements) · [Usage](references/patchers/claude-desktop-3p.md#usage) · [Verifying via main.log](references/patchers/claude-desktop-3p.md#verifying-it-worked) · [Registry schema](references/patchers/claude-desktop-3p.md#registry-schema-what-gets-written)
- **PATCH third-party apps**
  - **WHITEN LM Studio tray icon** — on-demand `apply` / `restore`; re-run after each LM Studio update ([detail](references/patchers/lm-studio-white-tray.md))
    - [How it works](references/patchers/lm-studio-white-tray.md#how-it-works) · [Usage](references/patchers/lm-studio-white-tray.md#usage) · [Customize icon](references/patchers/lm-studio-white-tray.md#customize-icon-design) · [Troubleshooting](references/patchers/lm-studio-white-tray.md#troubleshooting)
  - **INJECT markdown section into any file** — generic, idempotent ([detail](references/patchers/md-section-patcher.md))
    - [Worked example](references/patchers/md-section-patcher.md#worked-example)

