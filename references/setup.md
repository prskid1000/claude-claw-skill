# Installation & Troubleshooting Reference

---

## Python Packages

| pip name | import name | Purpose |
|----------|-------------|---------|
| `openpyxl` | `openpyxl` | Create/read/edit Excel .xlsx files (cells, styles, charts, formulas) |
| `python-docx` | `docx` | Create/read/edit Word .docx files (paragraphs, tables, styles, images) |
| `python-pptx` | `pptx` | Create/read/edit PowerPoint .pptx files (slides, shapes, charts, layouts) |
| `pymupdf` | `fitz` | PDF read, render, annotate, merge, split, extract text/images, page-to-image |
| `PyPDF2` | `PyPDF2` | PDF merge, split, rotate, encrypt/decrypt, extract text (simple ops) |
| `reportlab` | `reportlab` | Generate PDFs from scratch (precise layout, tables, charts, graphics) |
| `pdfplumber` | `pdfplumber` | Extract tables and text from PDFs with positional data |
| `pillow` | `PIL` | Image manipulation (resize, crop, rotate, filters, format convert, draw) |
| `lxml` | `lxml` | Fast XML/HTML parsing, XPath, XSLT, validation (XSD, RelaxNG, DTD) |
| `beautifulsoup4` | `bs4` | HTML/XML parsing with CSS selectors, tree navigation, modification |
| `pandas` | `pandas` | DataFrames for data analysis, CSV/Excel/JSON/SQL read/write |
| `matplotlib` | `matplotlib` | Charts and plots (line, bar, pie, scatter, histogram, subplots) |
| `requests` | `requests` | HTTP client (GET, POST, PUT, DELETE, sessions, auth, file upload) |
| `pyyaml` | `yaml` | Read/write YAML files |

### Install all
```bash
pip install openpyxl python-docx python-pptx pymupdf PyPDF2 reportlab pdfplumber pillow lxml beautifulsoup4 pandas matplotlib requests pyyaml
```

### Verify a package
```bash
python -c "import openpyxl; print(openpyxl.__version__)"
python -c "import fitz; print(fitz.__doc__)"
python -c "import docx; print('python-docx OK')"
```

---

## CLI Tools

| Tool | Check command | Install command (winget) | Purpose |
|------|--------------|------------------------|---------|
| `gws` | `gws --version` | `npm install -g @anthropic/gws` | Google Workspace CLI (Drive, Sheets, Docs, Slides, Gmail, Calendar) |
| `clickup` | `clickup version` | Download binary from [GitHub releases](https://github.com/triptechtravel/clickup-cli/releases) → `~/.local/bin/` | ClickUp task management (tasks, sprints, comments, time, git linking) |
| `git` | `git --version` | `winget install Git.Git` | Version control |
| `ffmpeg` | `ffmpeg -version` | `winget install Gyan.FFmpeg` | Video/audio processing, conversion, streaming |
| `pandoc` | `pandoc --version` | `winget install JohnMacFarlane.Pandoc` | Universal document converter (45+ input, 60+ output formats) |
| `magick` | `magick --version` | `winget install ImageMagick.ImageMagick` | CLI image processing (resize, convert, compose, batch) |
| `node` | `node --version` | `winget install OpenJS.NodeJS` | JavaScript runtime (required for npm-based tools) |
| `npm` | `npm --version` | (comes with node) | Package manager for JS/TS tools |

---

## MCP Servers

These MCPs are first-class `claude-claw` dependencies and are verified on every session by `scripts/healthcheck.py`. If a check fails, the healthcheck prints the exact fix to apply — it will not patch `~/.claude.json` automatically.

> **Windows note:** Do **not** manually wrap `npx` in `cmd /c` in your config. Claude Code's MCP launcher already spawns Windows MCP servers as `cmd.exe /d /s /c "npx ..."` internally. A manual wrapper causes double-wrapping.

### MySQL

Installed as a user-level MCP in `~/.claude.json` → `mcpServers.mcp_server_mysql`.

#### ~/.claude.json entry
```json
{
  "mcpServers": {
    "mcp_server_mysql": {
      "type": "stdio",
      "command": "npx",
      "args": ["@benborla29/mcp-server-mysql"],
      "env": {
        "MYSQL_HOST": "127.0.0.1",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASS": "password",
        "MYSQL_DB": "database_name",
        "ALLOW_INSERT_OPERATION": "true",
        "ALLOW_UPDATE_OPERATION": "true",
        "ALLOW_DELETE_OPERATION": "false",
        "MULTI_DB_WRITE_MODE": "true"
      }
    }
  }
}
```

#### Environment variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `MYSQL_HOST` | `127.0.0.1` | Database host |
| `MYSQL_PORT` | `3306` | Database port |
| `MYSQL_USER` | `root` | Username |
| `MYSQL_PASS` | (none) | Password |
| `MYSQL_DB` | (none) | Default database |

#### Install
```bash
npm install -g @benborla29/mcp-server-mysql
```

#### Verify
```python
mcp__mcp_server_mysql__mysql_query(query="SELECT 1 AS test")
# Expected: {"column_names": ["test"], "rows": [[1]]}
```

---

### Chrome DevTools

Installed via the `chrome-devtools-plugins` plugin marketplace, not via manual `mcpServers` config. The plugin ships its own `.mcp.json` at:

```
~/.claude/plugins/cache/chrome-devtools-plugins/chrome-devtools-mcp/latest/.mcp.json
```

Default content (do not modify — the healthcheck verifies it):
```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": ["chrome-devtools-mcp@latest"]
  }
}
```

Install / update the plugin via the Claude Code plugin manager. Verify with:
```python
mcp__plugin_chrome-devtools-mcp_chrome-devtools__list_pages()
```

#### Connect to an existing browser (advanced)
If you need to drive a specific, already-running browser instance (e.g. a pre-authenticated profile, or Edge), start the browser with a remote debugging port and point the MCP at it via `--browserUrl`:
```bash
# start browser (Chrome or Edge) with remote debugging
start chrome --remote-debugging-port=9222 --user-data-dir="C:/tmp/debug-profile"
# or: start msedge --remote-debugging-port=9222 --user-data-dir="C:/tmp/debug-profile"
```
Then override the plugin `.mcp.json` args to `["chrome-devtools-mcp@latest", "--browserUrl=http://127.0.0.1:9222"]` and restart Claude Code. Note: the `-e`/`--executablePath` flag is **not** a reliable way to redirect the MCP at a non-Chrome browser — Puppeteer's launch validation falls back to a bundled Chrome if the binary isn't recognized.

---

### ClickUp (CLI, not MCP)

This skill uses the standalone `clickup` CLI (installed via the CLI Tools table above), **not** an MCP server. Authenticate with:

```bash
clickup auth login           # interactive OAuth/API-token flow
clickup space select         # pick default workspace/space
```

See `references/clickup-cli.md` for the full command surface.

---

## GWS Authentication

### Login (interactive)
```bash
gws auth login
```
Opens browser for Google OAuth. Grant requested permissions for Drive, Sheets, Docs, Slides, Gmail, Calendar.

### Verify
```bash
gws auth status
gws drive about
```

### Token refresh
Tokens auto-refresh. If expired/revoked:
```bash
gws auth logout
gws auth login
```

### Multiple accounts
```bash
gws auth login --account work
gws auth login --account personal
gws --account work drive files list
```

---

## Troubleshooting

| Problem | Symptoms | Fix |
|---------|----------|-----|
| Python package not found | `ModuleNotFoundError: No module named 'xxx'` | `pip install PACKAGE_NAME` (use pip name, not import name) |
| Wrong pip/python | Package installs but still not found | Use `python -m pip install PACKAGE` to ensure correct environment |
| pymupdf import | `import fitz` fails | `pip install pymupdf` (pip name differs from import name) |
| python-docx import | `import docx` fails | `pip install python-docx` (not `docx`, which is a different package) |
| gws not found | `command not found: gws` | `npm install -g @anthropic/gws` then restart shell |
| gws auth expired | 401 errors from gws commands | `gws auth logout && gws auth login` |
| ffmpeg not found | `command not found: ffmpeg` | `winget install Gyan.FFmpeg` then restart shell |
| pandoc not found | `command not found: pandoc` | `winget install JohnMacFarlane.Pandoc` then restart shell |
| magick not found | `command not found: magick` | `winget install ImageMagick.ImageMagick` then restart shell |
| clickup not found | `command not found: clickup` | Download binary from [releases](https://github.com/triptechtravel/clickup-cli/releases) → `~/.local/bin/clickup.exe` |
| clickup auth failed | 401 or "not authenticated" | Run `clickup auth login` then `clickup space select` |
| MySQL MCP fails | Tool call returns connection error | Check MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS in `~/.claude.json`; verify MySQL is running |
| MySQL access denied | `Access denied for user` | Verify credentials; check user grants with `SHOW GRANTS FOR 'user'@'host'` |
| MCP config change not picked up | Edited `.mcp.json` or `~/.claude.json`, tool still uses old behavior | `.mcp.json` is read once at Claude Code startup. Fully quit Claude Code (including background `node.exe` processes for the MCP server), then relaunch |
| `cmd /c` warning on an mcpServers entry | Config linter flags "Windows requires 'cmd /c' wrapper" | Ignore it — Claude Code auto-wraps `npx` on Windows (`cmd.exe /d /s /c "npx ..."`). Adding a manual wrapper causes double-wrapping |
| Chrome DevTools MCP launches Chrome instead of a custom browser | `-e` / `--executablePath` flag is ignored | Puppeteer validates the binary and falls back to bundled Chrome silently. Use `--browserUrl` against a manually started browser instead (see the "Connect to an existing browser" section above) |
| npm global install fails | EACCES permission error | Run terminal as Administrator, or use `npx` instead of global install |
| PATH not updated | Tool installed but not found | Restart shell/terminal after installing CLI tools |
| Pandoc PDF fails | `pdflatex not found` | Install a LaTeX distribution (`winget install MiKTeX.MiKTeX`) or use `--pdf-engine=weasyprint` |
| Large file upload fails | Timeout on gws drive upload | Check file size; use resumable upload for files > 5MB |
| Pillow format error | Cannot identify image file | Verify file is not corrupt; check file extension matches actual format |
| openpyxl formula error | Formulas show as text | Ensure formula strings start with `=`; do not quote the formula |
| reportlab encoding | Unicode characters missing | Use a Unicode-capable font (register with `pdfmetrics.registerFont`) |
