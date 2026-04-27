# Test templates

Copy-paste skeletons for adding tests when a new verb (or new noun) is introduced.

## Adding a verb to an existing noun

1. Open `tests/unit/test_<noun>.py`.
2. Append a `class TestVerbName:` block — pattern:

```python
class TestVerbName:
    def test_minimum_args(self, runner, tmp_path, sample_xxx):
        ...
    def test_with_flag(self, runner, tmp_path, sample_xxx):
        ...
    def test_overwrite_protection(self, runner, tmp_path, sample_xxx):
        ...
```

See `verb_test_template.py` for the full pattern.

## Adding a new noun

1. Add the noun to `claw/__main__.NOUNS`.
2. Copy `verb_test_template.py` to `tests/unit/test_<noun>.py`.
3. Set `NOUN = "<noun>"`.
4. Add a `class TestVerb:` block per verb.

The `tests/coverage/` parametric tests pick up new nouns/verbs automatically
from the discovery walk in `_discovery.py`, so they need no edits.

## Adding an end-to-end flow

A flow exercises a multi-verb pipeline on real artifacts. Use when the new
verb participates in a meaningful chain (e.g. `csv → xlsx → pdf → drive`).

Copy `flow_test_template.py` to `tests/flows/test_flow_<area>.py` and fill in
each numbered stage method.

## Helpers reference (`tests/_helpers.py`)

| Helper                           | Purpose                                              |
|----------------------------------|------------------------------------------------------|
| `invoke(runner, *args)`          | Run `claw <args>` — asserts no traceback             |
| `assert_ok(res)`                 | Exit 0 + dumps stdout on failure                     |
| `assert_exit(res, code)`         | Specific non-zero exit                               |
| `assert_json_output(res)`        | Parse JSON stdout — returns parsed payload           |
| `require_tool(name)`             | **Fails** (not skips) if external tool missing       |
| `assert_pdf_pages(p, n)`         | Validate via PyMuPDF                                 |
| `assert_pdf_contains(p, needle)` | Page-text contains needle                            |
| `assert_xlsx_sheets(p, names)`   | Validate via openpyxl                                |
| `assert_xlsx_cell(p, s, c, v)`   | A1-style cell value check                            |
| `assert_docx_has_text(p, n)`     | Paragraph text contains needle                       |
| `assert_docx_heading(p, t, lvl)` | Heading present                                      |
| `assert_pptx_slides(p, n)`       | Slide count                                          |
| `assert_image_dims(p, w, h)`     | Pillow dim check                                     |
| `assert_image_format(p, "PNG")`  | Pillow format check                                  |
| `assert_video_duration(p, s)`    | ffprobe — call `require_tool("ffprobe")` first       |
| `local_http_server(dir)`         | Context manager → `http://127.0.0.1:<port>`          |
| `make_yaml_pipeline(p, steps)`   | Write a recipe                                       |

## Fixture catalog (`conftest.py`)

| Fixture                | Yields                          | Notes                                       |
|------------------------|---------------------------------|---------------------------------------------|
| `runner`               | `CliRunner`                     |                                             |
| `sample_csv`           | factory → `Path` to `.csv`      | `(rows=3, name=, header=)`                  |
| `sample_xlsx`          | factory → `Path` to `.xlsx`     | `(name=, sheet="Data", rows=)`              |
| `sample_pdf`           | factory → `Path` to `.pdf`      | `(name=, pages=2, text=)`                   |
| `sample_pdf_multipage` | factory → 5-page `.pdf`         | per-page `PAGE_MARKER_<N>`                  |
| `sample_png`           | factory → `Path` to `.png`      | `(size=(100,100), color=)`                  |
| `sample_jpg`           | factory → `Path` to `.jpg`      |                                             |
| `sample_html`          | factory → minimal `.html`       |                                             |
| `sample_html_rich`     | factory → realistic article     | nav, table, image, script/style noise       |
| `sample_xml`           | factory → tiny `.xml`           |                                             |
| `sample_md`            | factory → minimal `.md`         |                                             |
| `sample_md_rich`       | factory → headings/list/table   | for `from-md` / `convert` flows             |
| `sample_json_rows`     | factory → `.json` array         |                                             |
| `sample_pptx`          | factory → `.pptx`               | `(slides=1)`                                |
| `sample_docx`          | factory → `.docx`               |                                             |
| `sample_mp4`           | factory → `.mp4` via ffmpeg     | requires ffmpeg (fails loudly)              |
| `sample_wav`           | factory → `.wav` via ffmpeg     | requires ffmpeg                             |
| `sample_yaml_pipeline` | factory → recipe `.yaml`        | optional `steps=[...]` override             |

## External-tool policy

`require_tool(name)` **raises AssertionError** when missing — no silent skips.
This forces the developer to run `python ~/.claude/skills/claude-claw/scripts/healthcheck.py --install`
when CI fails.

Tools used: `pandoc`, `ffmpeg`, `ffprobe`, `magick`, `tesseract`, `qpdf`,
`soffice` (LibreOffice), `gws`.
