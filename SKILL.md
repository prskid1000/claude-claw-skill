---
name: claude-claw
description: >
  Reference guide for documents, spreadsheets, presentations, PDFs, images, video, audio,
  Google Workspace, ClickUp, MySQL, and media processing.
---

# Claude Claw — Productivity OS

## Contents

1. [Bootstrap](#bootstrap)
2. [Workflow](#workflow)
3. [Windows Notes](#windows-notes)
4. [References](#references)
5. [Examples](#examples)
6. [Scripts](#scripts)
7. [Quick Decision Tree](#quick-decision-tree)

## Bootstrap

```bash
python ~/.claude/skills/claude-claw/scripts/healthcheck.py
```

## Workflow

`Source -> Transform (Python) -> Output (/tmp/) -> Deliver (gws)`

## Windows Notes

On Windows, `gws` and `clickup` are `.cmd` shims that `subprocess.run(["gws", ...])` cannot find directly. Use `shutil.which()` to resolve the full path first:

```python
import shutil, subprocess
gws = shutil.which("gws")
subprocess.run([gws, "drive", "files", "list"], capture_output=True, text=True)
```

Alternatively, call `node` with the JS entry point directly.

## References

| Topic | File | Contents |
|-------|------|----------|
| Google Workspace CLI | [references/gws-cli.md](references/gws-cli.md) | Drive, Sheets, Docs, Slides, Gmail, Calendar, Tasks CLI commands (~1300 lines) |
| Document creation | [references/document-creation.md](references/document-creation.md) | openpyxl, python-docx, python-pptx API reference (~1900 lines) |
| PDF tools | [references/pdf-tools.md](references/pdf-tools.md) | PyMuPDF, PyPDF2, pdfplumber, reportlab (~2100 lines) |
| Media tools | [references/media-tools.md](references/media-tools.md) | Pillow, ImageMagick CLI, FFmpeg CLI (~1800 lines) |
| Document conversion | [references/conversion-tools.md](references/conversion-tools.md) | Pandoc (45+ input, 60+ output formats) (~500 lines) |
| HTML/XML parsing | [references/web-parsing.md](references/web-parsing.md) | lxml, BeautifulSoup4 (~680 lines) |
| Email / MIME | [references/email-reference.md](references/email-reference.md) | Python MIME composition, Gmail CLI helpers (~260 lines) |
| ClickUp CLI | [references/clickup-cli.md](references/clickup-cli.md) | ClickUp task/list/space CLI commands (~310 lines) |
| Setup | [references/setup.md](references/setup.md) | Installation guide (pip, CLI, GWS auth, MCP, LSP) (~220 lines) |
| Claude patcher | [references/claude-patcher.md](references/claude-patcher.md) | Claude Code binary patcher (~60 lines) |

## Examples

| Task | File | Contents |
|------|------|----------|
| Office documents | [examples/office-documents.md](examples/office-documents.md) | Excel, Word, PowerPoint working examples (~2150 lines) |
| PDF workflows | [examples/pdf-workflows.md](examples/pdf-workflows.md) | PDF generation, editing, extraction (~1420 lines) |
| Google Workspace | [examples/google-workspace.md](examples/google-workspace.md) | GWS CLI practical examples (~110 lines) |
| Image processing | [examples/image-processing.md](examples/image-processing.md) | Pillow workflows (~510 lines) |
| Video / audio | [examples/video-audio.md](examples/video-audio.md) | FFmpeg workflows (~430 lines) |
| Email workflows | [examples/email-workflows.md](examples/email-workflows.md) | MIME composition, Gmail sending (~450 lines) |
| Data pipelines | [examples/data-pipelines.md](examples/data-pipelines.md) | Multi-step data transformation (~670 lines) |
| Document conversion | [examples/document-conversion.md](examples/document-conversion.md) | Pandoc conversion examples (~730 lines) |
| ClickUp workflows | [examples/clickup-workflows.md](examples/clickup-workflows.md) | Task management workflows (~210 lines) |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/healthcheck.py](scripts/healthcheck.py) | Verify packages, CLI tools, MCP servers, and skill structure |
| [scripts/claude-patcher.js](scripts/claude-patcher.js) | Claude Code binary patcher |

## Quick Decision Tree

- **CREATE a document?** → [references/document-creation.md](references/document-creation.md) (Excel/Word/PPT) or [references/pdf-tools.md](references/pdf-tools.md) (PDF)
- **CONVERT between formats?** → [references/conversion-tools.md](references/conversion-tools.md) (Pandoc)
- **SEND email?** → [references/email-reference.md](references/email-reference.md) (MIME + Gmail)
- **USE Google Drive/Sheets/Docs?** → [references/gws-cli.md](references/gws-cli.md)
- **PROCESS images?** → [references/media-tools.md](references/media-tools.md) (Pillow section)
- **PROCESS video/audio?** → [references/media-tools.md](references/media-tools.md) (FFmpeg section)
- **PARSE HTML/XML?** → [references/web-parsing.md](references/web-parsing.md)
- **MANAGE tasks?** → [references/clickup-cli.md](references/clickup-cli.md)
- **Need WORKING CODE to copy?** → `examples/` folder
