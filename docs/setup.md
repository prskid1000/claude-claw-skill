# Setup — Install & Troubleshoot

> Install missing tools, packages, MCP servers. Auto-fix where possible, guide where not.

**Related:** [database-workflows.md](database-workflows.md) | [gws-quickref.md](gws-quickref.md)

---

## Quick Verify

```bash
python ~/.claude/skills/cortex/bin/healthcheck.py
```

## Python Packages

```bash
# All at once
pip install openpyxl python-docx python-pptx pymupdf PyPDF2 reportlab pdfplumber pillow lxml beautifulsoup4

# Individual
pip install openpyxl          # Excel .xlsx        → import openpyxl
pip install python-docx       # Word .docx         → import docx
pip install python-pptx       # PowerPoint .pptx   → import pptx
pip install pymupdf           # PDF read/edit      → import fitz
pip install PyPDF2            # PDF merge/split    → import PyPDF2
pip install reportlab         # PDF generation     → import reportlab
pip install pdfplumber        # PDF table extract  → import pdfplumber
pip install pillow            # Image manipulation → import PIL
pip install lxml              # XML/HTML parsing   → import lxml
pip install beautifulsoup4    # Web scraping       → import bs4

# Optional
pip install pandas matplotlib requests pyyaml
```

**Auto-install pattern** (used by healthcheck.py):
```python
try:
    import module
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "package-name"])
```

## CLI Tools

| Tool | Check | Install (Windows) |
|------|-------|-------------------|
| `gws` | `gws --version` | `npm install -g @nicholasgriffintn/google-workspace-cli` |
| `git` | `git --version` | `winget install Git.Git` |
| `ffmpeg` | `ffmpeg -version` | `winget install ffmpeg` |
| `pandoc` | `pandoc --version` | `winget install JohnMacFarlane.Pandoc` |
| `magick` | `magick --version` | `winget install ImageMagick.ImageMagick` |
| `node/npm` | `node --version` | `winget install OpenJS.NodeJS` |

**Prerequisites:** `winget` (pre-installed on Windows 11) or `choco` (Chocolatey).

**Dependency chain:**
- MCP servers need `npm` → needs `Node.js`
- Pandoc PDF output needs `xelatex` → use pymupdf/reportlab instead if not installed

## MCP Servers

All configured in `~/.claude/settings.json` under `mcpServers`.

### MySQL

```json
{
  "mcpServers": {
    "mcp_server_mysql": {
      "command": "npx",
      "args": ["-y", "@benborla29/mcp-server-mysql"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "password",
        "MYSQL_DATABASE": "database_name"
      }
    }
  }
}
```

Install: `npm install -g @benborla29/mcp-server-mysql`
Verify: `mcp__mcp_server_mysql__mysql_query(query="SHOW DATABASES")`

### Chrome DevTools

```json
{
  "mcpServers": {
    "chrome-devtools-mcp": {
      "command": "npx",
      "args": ["-y", "@anthropic/chrome-devtools-mcp"]
    }
  }
}
```

Launch Edge with debugging: `"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222`

### ClickUp

```json
{
  "mcpServers": {
    "clickup": {
      "command": "npx",
      "args": ["-y", "@anthropic/clickup-mcp"],
      "env": { "CLICKUP_API_TOKEN": "pk_..." }
    }
  }
}
```

## GWS Authentication

```bash
# Interactive login (user must run manually)
# Tell user: ! gws auth login
# Verify:
gws drive files list --params '{"pageSize":1}'
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `pip install` permission error | `pip install --user package-name` |
| `winget` not found | Install App Installer from Microsoft Store |
| `npm` not found | Install Node.js: `winget install OpenJS.NodeJS` |
| GWS auth expired | `! gws auth login` |
| MCP won't start | Check `~/.claude/settings.json` for typos |
| MySQL connection refused | Verify host/port/credentials in env vars |
| Edge not found | Update path in DevTools launch command |
| FFmpeg not in PATH | Add install dir to system PATH, restart terminal |
| `magick` not found | Reinstall ImageMagick with "Install legacy utilities" checked |
| Pandoc PDF fails | LaTeX not installed — use pymupdf/reportlab instead |
