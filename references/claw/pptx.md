# `claw pptx` — PowerPoint Operations Reference

CLI wrapper over `python-pptx` for deck creation and manipulation.

## Contents

- **CREATE / EDIT**
  - [New deck](#11-new) · [Add slide](#12-add-slide) · [From outline](#13-from-outline)
- **INSERT OBJECTS**
  - [Add chart](#21-add-chart) · [Add table](#22-add-table) · [Add image](#23-add-image) · [Add shape](#24-add-shape) · [Fill placeholder](#25-fill)
- **ADVANCED**
  - [Brand template](#31-brand) · [Refresh charts](#32-chart-refresh) · [Speaker notes](#33-notes) · [Reorder slides](#34-reorder) · [Image crop](#35-image) · [Hyperlink](#36-link)
- **PROPERTIES**
  - [Core metadata](#41-meta)

---

## Critical Rules

1. **Slide Selection** — `--slide` accepts 1-based index.
2. **Template Survival** — Use `--template` on `new` to preserve corporate themes, masters, and styles.
3. **Chart Data** — `add-chart` requires a CSV/JSON data source to populate the embedded Excel sheet.

---

## 1.1 new
Create a blank `.pptx` or one based on a template.
```bash
claw pptx new <OUT_PPTX> [--template <FILE.pptx>] [--force]
```

## 1.2 add-slide
Append a new slide with optional title and layout.
```bash
claw pptx add-slide <SRC_PPTX> [--title <TEXT>] [--layout <INDEX>] [--force]
```

## 1.3 from-outline
Build a deck from a Markdown outline (H1 → title slide, H2 → content slide).
```bash
claw pptx from-outline <OUT> --data <FILE.md|-> [--template <FILE.pptx>] [--layout-title <N>] [--layout-body <N>] [--notes-from-blockquote]
```

---

## 2.1 add-chart
Insert a chart (bar, col, line, pie) into a slide.
```bash
claw pptx add-chart <SRC_PPTX> --slide <N> --type <TYPE> --data <FILE.csv> [--title <TEXT>] [--force]
```

## 2.2 add-table
Insert a table from CSV or JSON rows.
```bash
claw pptx add-table <SRC_PPTX> --slide <N> --data <FILE.csv|.json> [--force]
```

## 2.3 add-image
Insert a PNG or JPEG onto a slide.
```bash
claw pptx add-image <SRC_PPTX> --slide <N> --image <FILE> [--force]
```

## 2.4 add-shape
Draw a rectangle / oval / triangle / arrow / callout / line on a slide.
```bash
claw pptx add-shape <SRC_PPTX> --slide <N> --kind rect|oval|triangle|arrow|callout|line [--at x,y] [--size w,h] [--text <T>] [--fill #RRGGBB] [--line #RRGGBB]
```

## 2.5 fill
Write text into a placeholder (by index) or a named shape on a slide.
```bash
claw pptx fill <SRC_PPTX> <TEXT> --slide <N> (--placeholder <IDX> | --shape-name <NAME>)
```

---

## 3.1 brand
Apply a corporate template / master-slide to an existing deck.
```bash
claw pptx brand <SRC_PPTX> --template <FILE.pptx> [--force]
```

## 3.2 chart-refresh
Force PowerPoint to re-render charts linked to embedded data.
```bash
claw pptx chart-refresh <SRC_PPTX> [--force]
```

## 3.3 notes
Get or set speaker notes for a specific slide.
```bash
claw pptx notes <get|set> <SRC_PPTX> --slide <N> [--text <TEXT>]
```

## 3.4 reorder
Change slide sequence based on ID or index mapping.
```bash
claw pptx reorder <SRC_PPTX> --mapping <ID:NEW_INDEX,...> [--force]
```

## 3.5 image
Picture-shape operations on existing slide images.
```bash
claw pptx image crop <SRC_PPTX> --slide <N> --shape <NAME> --left <F> --right <F> --top <F> --bottom <F>
```

## 3.6 link
Manage hyperlinks on slide shapes (subcommand: `add`).
```bash
claw pptx link add <SRC_PPTX> --slide <N> --shape <NAME> --url <URL>
```

---

## 4.1 meta
Get or set core deck properties (title, author, subject, keywords, ...).
```bash
claw pptx meta get <SRC_PPTX> [--layouts] [--json]
claw pptx meta set <SRC_PPTX> [--title <T>] [--author <A>] [--subject <S>] [--keywords <K>]
```

---

## Footguns
- **Layout Indices** — Layout indices (0, 1, 2...) are template-specific. Use `claw pptx layouts` (internal) or inspect in PowerPoint.
- **SmartArt** — `python-pptx` cannot create or edit SmartArt.

## Escape Hatch
- [python-pptx docs](https://python-pptx.readthedocs.io/)

---

## Quick Reference
| Task | Command |
|------|---------|
| New Deck | `claw pptx new report.pptx` |
| Add Title Slide | `claw pptx add-slide report.pptx --title "Main"` |
| Add Table | `claw pptx add-table report.pptx --slide 2 --data t.csv` |
| Set Notes | `claw pptx notes set report.pptx --slide 1 --text "Speak loud"` |
