# `claw convert` — Document Format Conversion

Canonical CLI reference for `claw convert ...`. Thin ergonomic wrapper over `pandoc` (plus PyMuPDF for the LaTeX-free PDF path). Covers the 80% of Markdown/Word/HTML/PDF/EPUB/slides conversions where you don't need to hand-tune a Lua filter.

## Contents

- **SIMPLE** — one file, one format
  - [convert — extension-dispatched any↔any](#11-convert)
- **WITH FEATURES** — citations, TOC, styling, templates
  - [convert + feature flags (toc/template/css/math/bib/engine)](#21-convert-with-features)
- **BOOK** — long-form output
  - [convert book — chapter concatenation to pdf/epub/docx](#31-convert-book)
- **NO-LATEX PDF** — MD → PDF without a TeX install
  - [convert md2pdf-nolatex — PyMuPDF Story API](#41-convert-md2pdf-nolatex)
- **SLIDES** — decks
  - [convert slides — reveal.js / beamer / pptx](#51-convert-slides)
- **META** — discovery & defaults
  - [convert --list-input-formats / --list-output-formats / --defaults](#61-convert-meta)

---

## Critical Rules

1. **Safe-write default.** Every verb requires `--out FILE` (positional second arg is allowed for `convert`). If the target exists, the command refuses; add `--force` to overwrite or `--backup` to sidecar `.bak` the existing file.
2. **Selector syntax.**
   - **Pages** (applies to input PDF, output PDF post-slicing): `N | a-b | all | odd | even | z-1 | 1-5,7`. `z-1` = second-to-last.
   - **Colors** (CSS tokens in `--css` passthrough): `#RRGGBB`, `#RRGGBBAA`, named.
3. **`--json` on reads, `--dry-run` on writes.** `convert --list-*` emits arrays. `--dry-run` prints the underlying `pandoc` command (copy-pasteable) and exits without running.
4. **`--stream` for large books.** Emits one JSON progress line per chapter to stderr when running `convert book` — usable with `jq` for pipelines.
5. **Exit codes.** `0` success, `2` bad args / unknown format, `3` input missing, `4` output exists without `--force`, `5` pandoc error (stderr surfaced), `7` missing PDF engine / LaTeX package — with actionable hint.
6. **Self-documenting.** `claw convert --help` lists sub-verbs; `claw convert <verb> --help` prints the full flag table.
7. **Pandoc flag passthrough.** Anything after `--` is forwarded to pandoc verbatim: `claw convert in.md out.pdf -- --variable geometry=a4paper,margin=2cm`.

---

## 1.1 convert

Simple any↔any conversion. Format dispatched by the output extension — `.md .docx .html .pdf .epub .rst .tex .odt .rtf .org .pptx .ipynb .typ` all work out of the box.

```
claw convert <in> <out> [--from FMT] [--to FMT] [--standalone] [--embed-resources]
```

| Flag | Notes |
|---|---|
| `--from` | Override input format (useful for `.txt` that's actually Markdown) |
| `--to` | Override output format |
| `--standalone` / `-s` | Full document (header, styles); default on for html/tex/epub |
| `--embed-resources` | Inline images/CSS/JS into a single HTML file |

```
claw convert README.md README.html
claw convert notes.md notes.docx
claw convert article.docx article.md
claw convert sheet.csv sheet.html --from csv        # CSV table → HTML
```

---

## 2.1 convert (with features)

Same `convert` verb, plus optional feature flags. Flags stack — enable only what you need.

```
claw convert <in> <out>
    [--toc [--toc-depth N]]
    [--template FILE]
    [--ref-doc FILE.docx|.pptx]
    [--css FILE]
    [--mathjax | --katex]
    [--citeproc --bib FILE [--csl FILE]]
    [--engine xelatex|lualatex|pdflatex|weasyprint|typst|tectonic]
    [--highlight-style STYLE]
    [--number-sections]
    [--metadata KEY=VAL]
    [--variable KEY=VAL]
```

| Flag | Maps to pandoc | Notes |
|---|---|---|
| `--toc` + `--toc-depth` | `--toc --toc-depth=N` | Auto-generated table of contents |
| `--template` | `--template=FILE` | Override built-in Pandoc template |
| `--ref-doc` | `--reference-doc=FILE` | Style template for docx/pptx output |
| `--css` | `--css=FILE` | HTML/EPUB styling |
| `--mathjax` / `--katex` | `--mathjax` / `--katex` | HTML math rendering (mutex) |
| `--citeproc` | `--citeproc` | Enable citation processing |
| `--bib` | `--bibliography=FILE` | BibTeX / BibLaTeX / CSL-JSON / RIS |
| `--csl` | `--csl=FILE` | Citation Style Language stylesheet |
| `--engine` | `--pdf-engine=ENGINE` | PDF backend — see Critical Rules and [§ PDF Engines](../conversion-tools.md#pdf-engines) |
| `--highlight-style` | `--highlight-style=NAME` | Built-in: pygments, tango, kate, zenburn, breezedark, espresso, haddock, monochrome |

```
# TOC + KaTeX math
claw convert spec.md spec.html --toc --toc-depth 3 --katex

# Styled DOCX using a company template
claw convert report.md report.docx --ref-doc corporate-template.docx --toc

# Academic paper with citations
claw convert paper.md paper.pdf --citeproc --bib refs.bib --csl apa.csl --engine xelatex

# HTML with custom stylesheet, one file (images embedded)
claw convert post.md post.html --css style.css --embed-resources --standalone
```

---

## 3.1 convert book

Concatenate multiple Markdown chapters into a single output with shared metadata, TOC, and (optionally) bibliography.

```
claw convert book <chapters...> --out <OUT> [--title T] [--author A] [--metadata KEY=VAL]... [--toc] [--toc-depth N] [--csl FILE] [--bib FILE] [--css FILE] [--engine ENGINE] [--ref-doc FILE]
```

Chapters are concatenated in argument order. A top-level metadata block (`title`, `author`, `date`, `lang`, etc.) is injected from flags unless already present in the first chapter's YAML frontmatter.

Output format inferred from `--out`: `.pdf` `.epub` `.docx` `.html` all work. For EPUB, pass `--cover FILE` to set the cover image.

```
claw convert book intro.md ch01.md ch02.md ch03.md outro.md \
    --title "The Book" --author "Author Name" \
    --toc --toc-depth 2 --bib refs.bib --csl chicago.csl \
    --out book.pdf --engine xelatex

claw convert book chapters/*.md --cover cover.jpg --out book.epub

claw convert book drafts/*.md --out manuscript.docx --ref-doc template.docx
```

`--stream` emits one JSON line per chapter to stderr as it's processed — pipe to `jq` for progress bars.

---

## 4.1 convert md2pdf-nolatex

Markdown → PDF without needing a TeX distribution. Internally: `pandoc -t html5` with embedded CSS, then PyMuPDF's Story API renders the HTML to a paginated PDF. Trades fancy typography (ligatures, kerning) for zero install pain.

```
claw convert md2pdf-nolatex <in.md> <out.pdf> [--css FILE] [--page-size a4|letter] [--margin 2cm] [--font-family 'Inter,Arial,sans-serif']
```

| Flag | Default |
|---|---|
| `--page-size` | `a4` |
| `--margin` | `2cm` (all sides; accepts CSS units) |
| `--font-family` | `'Helvetica,Arial,sans-serif'` |
| `--css` | built-in minimal stylesheet; `--css FILE` replaces it |

```
claw convert md2pdf-nolatex README.md README.pdf
claw convert md2pdf-nolatex report.md report.pdf --css house-style.css --page-size letter
```

Use when:
- A full LaTeX install is not available / wanted.
- Output is for review / sharing, not print-shop typography.
- You want fast turnarounds on a CI runner without a TeX image.

Don't use when:
- You need precise math layout (LaTeX is still the gold standard).
- The output goes to a journal with a template.
- You need custom fonts embedded via `@font-face` with complex rules (WeasyPrint handles this better — use `--engine weasyprint` on the normal `convert` path).

---

## 5.1 convert slides

Markdown → slide deck in three flavors. Slide separation by `---` (horizontal rule) or heading level (`--slide-level N`, default `2`).

```
claw convert slides <in.md> --format reveal|beamer|pptx --out <OUT> [--theme T] [--ref-doc FILE.pptx] [--slide-level N]
```

| `--format` | Output extension | Themes |
|---|---|---|
| `reveal` | `.html` | `beige`, `black`, `blood`, `league`, `moon`, `night`, `serif`, `simple`, `sky`, `solarized`, `white` |
| `beamer` | `.pdf` (via LaTeX) | `AnnArbor`, `Berlin`, `Copenhagen`, `Darmstadt`, `Frankfurt`, `Madrid`, `Montpellier`, `Singapore`, `Warsaw`, `default` |
| `pptx` | `.pptx` | Use `--ref-doc template.pptx` for brand styling |

```
claw convert slides talk.md --format reveal --theme moon --out talk.html
claw convert slides talk.md --format beamer --theme Madrid --out talk.pdf
claw convert slides talk.md --format pptx --ref-doc brand.pptx --out talk.pptx
```

---

## 6.1 convert (meta)

Discovery and defaults-file passthrough.

```
claw convert --list-input-formats [--json]
claw convert --list-output-formats [--json]
claw convert --list-extensions [FORMAT] [--json]
claw convert --defaults <FILE.yaml>                # forward a Pandoc defaults YAML
```

`--defaults FILE.yaml` shells out to `pandoc --defaults FILE.yaml` after basic schema validation. The defaults file itself is canonical Pandoc YAML — see [pandoc defaults files](../conversion-tools.md#defaults-files).

```
claw convert --list-input-formats --json | jq '. | length'
claw convert --defaults build-site.yaml
```

---

## Footguns (why each verb exists)

- **Pandoc PDF requires a full LaTeX.** Missing packages surface as cryptic errors (`! LaTeX Error: File 'amsfonts.sty' not found`). `claw doctor --tool pandoc` probes for `amsfonts`, `unicode-math`, `booktabs`, `geometry`, `fontspec`, `xcolor` and prints actionable install hints (`tlmgr install amsfonts` on TeX Live, MiKTeX console on Windows). Exit code `7` on missing packages.
- **LaTeX is heavy.** If all you need is simple styling, route through `--engine weasyprint` (HTML+CSS, 100 MB install) or `--engine typst` (single binary, ~30 MB) or the `md2pdf-nolatex` verb (PyMuPDF, already installed). `claw convert in.md out.pdf --engine typst` is a drop-in replacement for a surprising fraction of use cases.
- **`--reference-doc` vs `--template` confusion.** `--ref-doc` is for docx/pptx — it's a *styled Word/PPT document* whose styles are copied. `--template` is for text formats (HTML, LaTeX, reveal.js) — a *text template* with `$variable$` placeholders. Mixing them silently fails. `claw convert` errors out if the extension doesn't match the flag.
- **Citeproc needs `--citeproc` enabled explicitly.** `--bib refs.bib` without `--citeproc` is silently ignored. `claw convert` warns on stderr if `--bib` is passed without `--citeproc`.
- **Slide-level default varies by output.** Pandoc defaults to the first heading level with content. Be explicit: `--slide-level 2`.
- **Reveal.js CDN default.** Built-in template references `https://unpkg.com/reveal.js/` — breaks offline. Pass `-- -V revealjs-url=./reveal.js/` (passthrough) to point at a local copy.

## Do-not-wrap list

The following belong in raw `pandoc`, not `claw convert`:

- **Custom Lua filter authoring.** Filter development is a text-editing task, not a CLI task. Write the filter, then apply it with `claw convert in.md out.pdf -- --lua-filter=my.lua`.
- **Pandoc defaults YAML authoring.** Use `--defaults FILE.yaml` to forward the file; don't invent flags that mirror every YAML key.
- **Custom reader / writer authoring** (pandoc's Lua reader/writer API). Niche; use pandoc directly.
- **Syntax highlighting theme authoring** (pandoc's `.theme` KDE files). Use the built-in names; override via raw pandoc for custom themes.

## When `claw` isn't enough

Drop to the underlying tool and look at its reference:

- Full pandoc flag / extension / filter reference: [../conversion-tools.md](../conversion-tools.md).
- PDF engines comparison: [../conversion-tools.md § PDF Engines](../conversion-tools.md#pdf-engines).
- Markdown extension list: [../conversion-tools.md § Extensions System](../conversion-tools.md#extensions-system).

Rule of thumb: if you need `--lua-filter`, multiple filters in order, or fine-tuned per-format behavior via a YAML defaults file — call `pandoc` directly (or use `claw convert ... -- <pandoc-flags>` for one-offs).

---

## Quick Reference

| Task | Command |
|---|---|
| MD → DOCX | `claw convert in.md out.docx` |
| MD → styled DOCX | `claw convert in.md out.docx --ref-doc template.docx --toc` |
| MD → HTML with KaTeX | `claw convert in.md out.html --katex --standalone --embed-resources` |
| MD → PDF (LaTeX) | `claw convert in.md out.pdf --engine xelatex --toc` |
| MD → PDF (no LaTeX) | `claw convert md2pdf-nolatex in.md out.pdf` |
| MD → PDF (HTML engine) | `claw convert in.md out.pdf --engine weasyprint --css style.css` |
| MD → EPUB | `claw convert in.md out.epub --toc` |
| DOCX → MD | `claw convert in.docx out.md` |
| Book (multi-chapter PDF) | `claw convert book ch*.md --title 'Book' --toc --out book.pdf --engine xelatex` |
| Reveal.js slides | `claw convert slides in.md --format reveal --theme moon --out talk.html` |
| Beamer PDF slides | `claw convert slides in.md --format beamer --out talk.pdf` |
| Paper with citations | `claw convert in.md out.pdf --citeproc --bib refs.bib --csl apa.csl` |
| List output formats | `claw convert --list-output-formats --json` |
