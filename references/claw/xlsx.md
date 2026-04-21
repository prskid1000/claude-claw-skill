# `claw xlsx` — Excel Operations Reference

CLI wrapper over `openpyxl` for spreadsheet work. Every verb is safe-by-default, emits structured output, and degrades gracefully on Windows-locked files.

## Contents

- **CREATE a workbook**
  - [New blank workbook](#11-new) · [From CSV](#12-from-csv) · [From JSON](#13-from-json) · [From HTML table](#14-from-html) · [From PDF tables](#15-from-pdf)
- **READ / EXTRACT data**
  - [Dump cells / ranges](#21-read) · [Export sheet to CSV](#22-to-csv) · [Export workbook to PDF](#23-to-pdf) · [SQL over sheets](#24-sql) · [Column statistics](#25-stat)
- **EDIT cells & objects**
  - [Append rows / sheets](#31-append) · [Rich text runs](#32-richtext) · [Embed images](#33-image)
- **FORMAT / STYLE**
  - [Apply styles](#41-style) · [Freeze panes](#42-freeze) · [Auto-filter](#43-filter) · [Conditional formatting](#44-conditional) · [Number format](#45-format) · [Excel tables](#46-table) · [Charts](#47-chart)
- **VALIDATE & structure**
  - [Dropdowns / constraints](#51-validate) · [Defined names](#52-name) · [Print setup](#53-print-setup)
- **PROTECT**
  - [Sheet / workbook passwords](#61-protect)
- **META**
  - [Get / set core properties](#71-meta) · [List pivots](#72-pivots)

---

## Critical Rules

1. **Memory Usage** — Large files (>50MB) can consume significant RAM; use `read` with `--range` to limit data.
2. **Formula Calculation** — `openpyxl` does not calculate formulas. It only reads the cached value or writes the formula string.
3. **LibreOffice Requirement** — `to-pdf` requires `soffice` (LibreOffice) to be in the system PATH.
4. **Range Syntax** — Always use standard A1 notation (e.g., `A1:D100`).

---

## 1.1 new
Create a blank `.xlsx`.
```bash
claw xlsx new <OUT_XLSX> [--sheet NAME]... [--force]
```

## 1.2 from-csv
Build a workbook from one or more CSVs.
```bash
claw xlsx from-csv <OUT_XLSX> <CSV>... [--sheet NAME] [--delimiter CHAR] [--encoding TEXT]
```

## 1.3 from-json
Build a workbook from a JSON array of row objects.
```bash
claw xlsx from-json <OUT_XLSX> --data <FILE.json> [--sheet NAME] [--force]
```

## 1.4 from-html
Parse HTML tables and write each as a sheet in `<OUT_XLSX>`.
```bash
claw xlsx from-html <OUT_XLSX> <SRC_HTML> [--force]
```

## 1.5 from-pdf
Convert PDF tables to sheets via `pdfplumber`.
```bash
claw xlsx from-pdf <OUT_XLSX> <SRC_PDF> [--force]
```

---

## 2.1 read
Print cell values as JSON (default), CSV, or TSV.
```bash
claw xlsx read <SRC_XLSX> [--sheet NAME] [--range A1:B10] [--json|--csv|--tsv]
```

## 2.2 to-csv
Export a sheet to CSV.
```bash
claw xlsx to-csv <SRC_XLSX> --sheet <NAME> [--out <FILE.csv>] [--force]
```

## 2.3 to-pdf
Render xlsx to PDF via LibreOffice (soffice) headless.
```bash
claw xlsx to-pdf <SRC_XLSX> <OUT_PDF> [--force]
```

## 2.4 sql
Run SQL over sheets (DuckDB if available, else SQLite).
```bash
claw xlsx sql <SRC_XLSX> <QUERY> [--out <FILE.csv|.xlsx>] [--json] [--force]
```

## 2.5 stat
Report min / max / mean / stddev / distinct / null counts per column.
```bash
claw xlsx stat <SRC_XLSX> --sheet <NAME> [--range A1:B10]
```

---

## 3.1 append
Append rows from a CSV/JSON file (or stdin) to a sheet.
```bash
claw xlsx append <SRC_XLSX> --sheet <NAME> --data <FILE.csv|.json> [--force]
```

## 3.2 richtext
Apply rich-text formatting to cells.
```bash
claw xlsx richtext <SRC_XLSX> --sheet <NAME> --cell <A1> --data <JSON_RUNS>
```

## 3.3 image
Embed images into a worksheet.
```bash
claw xlsx image <SRC_XLSX> --sheet <NAME> --image <FILE.png> --anchor <A1> [--width N] [--height N]
```

---

## 4.1 style
Apply font / fill / border / alignment to every cell in `--range`.
```bash
claw xlsx style <SRC_XLSX> --sheet <NAME> --range <A1:B10> [--bold] [--italic] [--color #RRGGBB] [--fill #RRGGBB] [--force]
```

## 4.2 freeze
Freeze the top N rows and/or left N columns.
```bash
claw xlsx freeze <SRC_XLSX> --sheet <NAME> [--rows N] [--cols N] [--force]
```

## 4.3 filter
Turn auto-filter on (or `--off`) for a range.
```bash
claw xlsx filter <SRC_XLSX> --sheet <NAME> --range <A1:B10> [--off] [--force]
```

## 4.4 conditional
Add one conditional-formatting rule.
```bash
claw xlsx conditional <SRC_XLSX> --sheet <NAME> --range <A1:B10> [--cell-is CONDITION] [--fill #RRGGBB] [--force]
```

## 4.5 format
Set `cell.number_format` on every cell in `--range`.
```bash
claw xlsx format <SRC_XLSX> --sheet <NAME> --range <A1:B10> --number-format <FMT> [--force]
```

## 4.6 table
Register an Excel Table over a range.
```bash
claw xlsx table <SRC_XLSX> --sheet <NAME> --range <A1:B10> --name <TABLE_NAME> [--force]
```

## 4.7 chart
Add a bar / col / line / pie / scatter / area chart.
```bash
claw xlsx chart <SRC_XLSX> --sheet <NAME> --type <TYPE> --data <RANGE> [--title TEXT] [--force]
```

---

## 5.1 validate
Add a list / whole / decimal / date / time / textLength / custom rule.
```bash
claw xlsx validate <SRC_XLSX> --sheet <NAME> --range <A1:B10> --type <TYPE> [--values TEXT] [--force]
```

## 5.2 name
Manage defined names in the workbook.
```bash
claw xlsx name <add|delete|list> <SRC_XLSX> [--name <NAME>] [--refers-to <REF>]
```

## 5.3 print-setup
Set print area, repeat titles, fit-to-page, orientation, paper size.
```bash
claw xlsx print-setup <SRC_XLSX> --sheet <NAME> [--print-area RANGE] [--orientation portrait|landscape] [--force]
```

---

## 6.1 protect
Apply or clear sheet/workbook password protection.
```bash
claw xlsx protect <SRC_XLSX> --scope <sheet|workbook> [--sheet NAME] --password <PW> [--force]
```

---

## 7.1 meta
Read or write core workbook properties (title, creator, etc.).
```bash
claw xlsx meta <get|set> <SRC_XLSX> [--property KEY] [--value VAL]
```

## 7.2 pivots
List or inspect pivot tables (read-only).
```bash
claw xlsx pivots list <SRC_XLSX> [--sheet NAME] [--json]
```

---

## Footguns
- **Formula Values** — Reading a cell with a formula returns the formula itself unless the file was saved by Excel with cached results.
- **Large Styles** — Applying unique styles to thousands of individual cells can inflate file size significantly; use `table` or named styles when possible.

## Escape Hatch
Underlying library: `openpyxl` (Python). For complex logic, write a Python script using `openpyxl` and run it via `python`.

## Quick Reference Table
| Task | Command |
|------|---------|
| New File | `claw xlsx new data.xlsx` |
| Import CSV | `claw xlsx from-csv data.xlsx raw.csv` |
| Read Cells | `claw xlsx read data.xlsx --range A1:B10` |
| Apply Style | `claw xlsx style data.xlsx --range A1:Z1 --bold` |
| Export PDF | `claw xlsx to-pdf data.xlsx report.pdf` |
