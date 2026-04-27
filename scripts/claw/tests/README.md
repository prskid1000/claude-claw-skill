# claw test suite

Pytest suite for the `claw` CLI. Three layers: parametric coverage (every
verb/flag/help), per-noun unit tests, and end-to-end flow tests.

## Run

```bash
# From scripts/claw/
pytest                      # full suite
pytest tests/coverage/      # mechanical coverage layer only
pytest tests/unit/          # per-noun unit tests
pytest tests/flows/ -v      # end-to-end pipelines, verbose
pytest -k xlsx              # everything xlsx-related
pytest -m flow              # flow tests only
pytest --no-network         # skip @pytest.mark.network
```

## Layout

```
tests/
├── _helpers.py              shared invoke / assert / artifact validators
├── _discovery.py            walks NOUNS×VERBS for parametric coverage
├── conftest.py              shared fixtures (sample_csv, sample_xlsx, ...)
├── test_common.py           direct unit tests for claw.common helpers
├── coverage/                mechanical, parametric coverage
│   ├── test_help_coverage.py     every noun + verb has --help
│   ├── test_runtime_coverage.py  every verb invokable without traceback
│   └── test_param_coverage.py    every --flag visible in --help
├── unit/                    per-noun, class-per-verb unit tests
│   ├── test_xlsx.py  test_docx.py  test_pptx.py  test_pdf.py
│   ├── test_img.py   test_media.py  test_convert.py
│   ├── test_doc.py   test_drive.py  test_email.py
│   ├── test_web.py   test_html.py   test_xml.py
│   ├── test_browser.py  test_pipeline.py  test_system.py
└── flows/                   end-to-end multi-verb pipelines on real artifacts
    ├── test_flow_xlsx_report.py        csv → xlsx → styled → chart
    ├── test_flow_pdf_pipeline.py       md → pdf → merge/split/wm/encrypt
    ├── test_flow_docx_authoring.py     new → headings → table → image → toc
    ├── test_flow_pptx_deck.py          outline → from-outline → table/chart
    ├── test_flow_image_pipeline.py     png → resize → enhance → webp/jpeg
    ├── test_flow_media_pipeline.py     mp4 → trim → scale → audio → gif
    ├── test_flow_web_html.py           local server → fetch → sanitize
    ├── test_flow_convert_chain.py      md → html → docx → pdf
    └── test_flow_yaml_pipeline.py      validate → graph → run a real recipe
└── templates/               copy-paste skeletons for new tests
    ├── README.md
    ├── verb_test_template.py
    └── flow_test_template.py
```

## External-tool policy: fail, don't skip

Tests use `require_tool("ffmpeg")` (and `pandoc`, `magick`, `tesseract`,
`qpdf`, `soffice`, `gws`) which **raises AssertionError** when the tool is
missing. We deliberately don't `pytest.skip` — silent skips let regressions
ship. Run `python ~/.claude/skills/claude-claw/scripts/healthcheck.py --install`
to bootstrap the environment.

## Adding a verb (workflow)

1. Open `tests/unit/test_<noun>.py` (or copy `tests/templates/verb_test_template.py`).
2. Append a `class TestVerbName:` block.
3. The discovery-driven parametric tests in `tests/coverage/` pick up the new
   verb automatically — no edits needed there.

See `tests/templates/README.md` for full template guidance.

## Flow tests use subprocess, not CliRunner

`invoke_subprocess()` runs each verb in a fresh interpreter. Slower
(~100ms cold-start per call), but on Windows it cleanly releases all OS
handles between calls — necessary because chained in-place writes to the
same xlsx file via in-process CliRunner can leak ZipFile mmaps and break
subsequent `os.replace`s.

Unit tests still use the in-process `invoke()` (CliRunner) — fast, and
each unit test starts with a fresh fixture so handle-leaks don't cross
test boundaries.

## No real external APIs

Drive, Docs, Gmail tests use `--help` and `--dry-run` only. The web tests
spin up a `http.server` on `127.0.0.1:<random>` so no network is required.
