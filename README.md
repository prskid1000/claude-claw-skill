# Claude Claw

A Claude Code skill that turns Claude into a productivity OS — a single library for working with documents (Excel, Word, PowerPoint, PDF), images, video/audio, Google Workspace, ClickUp, MySQL, email composition, and document conversion.

> **For agents:** start at [SKILL.md](SKILL.md) — it has the full file map with direct links to every section in every reference and example file.

## What's Inside

| Folder | Contents | Total |
|--------|----------|-------|
| `references/` | API/CLI documentation for each tool | ~6,000 lines across 10 files (+ 4 patcher refs) |
| `examples/` | Copy-paste runnable workflows | ~5,000 lines across 9 files |
| `scripts/` | Healthcheck + launch wrappers + patchers for third-party apps | healthcheck, 4 wrappers, 4 patchers |

**Tools covered:** openpyxl · python-docx · python-pptx · PyMuPDF · PyPDF2 · pdfplumber · reportlab · Pillow · ImageMagick · FFmpeg · Pandoc · lxml · BeautifulSoup4 · gws (Google Workspace) · clickup · MIME/Gmail.

## Install

```bash
git clone https://github.com/prskid1000/claude-claw-skill.git ~/.claude/skills/claude-claw
python ~/.claude/skills/claude-claw/scripts/healthcheck.py
```

The healthcheck verifies all dependencies and auto-fixes Windows LSP issues.

## Activate in Claude Code

The skill auto-loads when Claude detects a relevant task (creating a document, sending email, working with Google Workspace, etc.). To force-activate, mention `claude-claw` in your prompt or invoke `/claude-claw`.

## Optional: LSP-First Code Navigation + Auto-Load

To auto-load the File Map and LSP-first code-navigation rules on every conversation, install the canonical block into your global `~/.claude/CLAUDE.md` via the markdown section patcher:

```bash
python ~/.claude/skills/claude-claw/scripts/patchers/md-section-patcher.py apply \
  --target ~/.claude/CLAUDE.md \
  --section claude-claw \
  --source ~/.claude/skills/claude-claw/references/patchers/claude-md-block.md
```

The block is wrapped in `<!-- claude-claw:begin -->` / `<!-- claude-claw:end -->` markers and prepended to the top of your file; re-runs are idempotent. See [references/setup.md](references/setup.md#claudemd-integration) and [references/patchers/md-section-patcher.md](references/patchers/md-section-patcher.md) for details.

## Structure

```
claude-claw/
├── SKILL.md                    # File map index (auto-loaded into Claude's context)
├── README.md                   # This file
├── scripts/
│   ├── healthcheck.py          # Verify all deps + auto-fix Windows LSP
│   ├── _TEMPLATE.py            # Template for new scripts
│   ├── patchers/               # Binary/config patchers for third-party apps
│   │   ├── claude-patcher.js       # Claude Code binary patcher (context/output)
│   │   ├── claude-desktop-3p.py    # Claude Desktop 3P/BYOM registry toggle
│   │   ├── lm-studio-white-tray.py # LM Studio tray-icon whitener
│   │   └── md-section-patcher.py   # Idempotent markdown-section injector
│   └── wrappers/               # Local-model launch wrappers (codel / claudel / claudedl / codexl)
├── references/
│   ├── _TEMPLATE.md            # Template for new reference files
│   ├── gws-cli.md              # Google Workspace CLI (Drive/Sheets/Docs/Slides/Gmail/Calendar)
│   ├── document-creation.md    # Excel, Word, PowerPoint APIs
│   ├── pdf-tools.md            # PyMuPDF, PyPDF2, pdfplumber, reportlab
│   ├── media-tools.md          # Pillow, ImageMagick, FFmpeg
│   ├── conversion-tools.md     # Pandoc (45+ input, 60+ output formats)
│   ├── web-parsing.md          # lxml + BeautifulSoup4
│   ├── email-reference.md      # Python MIME composition
│   ├── clickup-cli.md          # ClickUp task management
│   ├── claude-customization.md # Launch wrappers + patcher overview
│   ├── patchers/               # Per-patcher reference docs
│   │   ├── claude-patcher.md       # Claude Code binary patcher
│   │   ├── claude-desktop-3p.md    # Claude Desktop 3P registry toggle
│   │   ├── lm-studio-white-tray.md # LM Studio tray-icon whitener
│   │   └── md-section-patcher.md   # Idempotent markdown-section injector
│   └── setup.md                # Installation guide
└── examples/
    ├── _TEMPLATE.md            # Template for new example files
    ├── office-documents.md     # Excel/Word/PowerPoint workflows
    ├── pdf-workflows.md        # PDF generation, editing, extraction
    ├── google-workspace.md     # GWS CLI examples
    ├── image-processing.md     # Pillow + ImageMagick workflows
    ├── video-audio.md          # FFmpeg workflows
    ├── email-workflows.md      # MIME composition + Gmail sending
    ├── data-pipelines.md       # CSV/PDF/DB → Excel/Sheets pipelines
    ├── document-conversion.md  # Pandoc conversions
    └── clickup-workflows.md    # Task management workflows
```

## Adding New Files

Templates are provided in `references/_TEMPLATE.md` and `examples/_TEMPLATE.md`. To add a new reference or example:

1. Copy the template into the appropriate folder
2. Replace placeholders
3. Add a link in [SKILL.md](SKILL.md) under the matching section
4. If it needs new dependencies, update `scripts/healthcheck.py` and `references/setup.md`

## Healthcheck

Run anytime to verify everything is set up:

```bash
python ~/.claude/skills/claude-claw/scripts/healthcheck.py
```

Checks: Python packages · CLI tools · Google Workspace auth · MCP servers (MySQL, Chrome DevTools) · LSP plugins (Pyright, TypeScript, jdtls, Kotlin). Auto-fixes the Windows LSP `uv_spawn` issue.

## License

MIT
