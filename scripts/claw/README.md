# claw

CLI wrapper around openpyxl / fitz / Pillow / python-docx / python-pptx / lxml / pandoc / ffmpeg / magick — absorbs the common glue so everyday document / media / web tasks collapse to one flag.

## Install

```bash
# from PyPI once published
uv tool install claw                  # preferred
pipx install claw                     # alt
pip install claw                      # works too

# from this repo (editable)
uv pip install -e ~/.claude/skills/claude-claw/scripts/claw
```

## Usage

```bash
claw --help                   # all nouns
claw xlsx --help              # verbs under xlsx
claw xlsx from-csv --help     # flags for a verb
claw help <cmd>               # alias
claw --help-all               # full tree dump
```

See the skill docs for the full reference: `references/claw/*.md`.

## Optional extras

Install only what you need:

```bash
uv tool install 'claw[xlsx,pdf]'
```

Available extras: `xlsx`, `docx`, `pptx`, `pdf`, `img`, `web`, `html`, `xml`, `pipeline`, `all`.
