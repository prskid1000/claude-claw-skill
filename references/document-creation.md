# Document Creation Libraries Reference

> **TL;DR: use `claw xlsx`, `claw docx`, `claw pptx` for everything in this file's covered branches.** See [references/claw/xlsx.md](claw/xlsx.md), [references/claw/docx.md](claw/docx.md), [references/claw/pptx.md](claw/pptx.md). This reference keeps the Python library API (`openpyxl`, `python-docx`, `python-pptx`) **only** for the escape-hatch surface `claw` deliberately doesn't wrap: parameter tables, enum / constant listings, length-unit helpers, and the Escape-hatch recipes at the end.

## Contents

- **CREATE / EDIT Excel (.xlsx)** — `openpyxl`
  - [Workbook & worksheet operations](#11-workbook--worksheet-operations) · [Cell operations](#12-cell-operations) · [Styling & formatting](#13-styling--formatting) · [Conditional formatting](#14-conditional-formatting) · [Data validation](#15-data-validation) · [Charts](#16-charts) · [Tables](#17-tables) · [Named ranges](#18-defined-names--named-ranges) · [Auto-filter](#19-auto-filter--sorting) · [Images](#110-images) · [Page setup](#111-page-setup--print) · [Worksheet protection](#112-worksheet-protection) · [Freeze panes](#113-freeze-panes) · [Col width / row height](#114-column-width--row-height)
- **CREATE / EDIT Word (.docx)** — `python-docx`
  - [Document operations](#21-document-operations) · [Paragraphs & runs](#22-paragraphs--runs) · [Headings & lists](#23-headings--lists) · [Tables](#24-tables) · [Images](#25-images) · [Sections & page layout](#26-sections--page-layout) · [Headers & footers](#27-headers--footers) · [Breaks](#28-breaks) · [Hyperlinks](#29-hyperlinks) · [Styles](#210-styles) · [Core properties](#211-core-properties) · [Length units](#212-length-units)
- **CREATE / EDIT PowerPoint (.pptx)** — `python-pptx`
  - [Presentation & slides](#31-presentation--slides) · [Shapes](#32-shapes) · [Text frames & formatting](#33-text-frames--formatting) · [Charts](#34-charts) · [Fill & line formatting](#35-fill--line-formatting) · [Placeholders](#36-placeholders) · [Slide background](#37-slide-background) · [Hyperlinks & click actions](#38-hyperlinks--click-actions) · [OLE embedding & media](#39-ole-embedding--media) · [Core properties](#310-core-properties) · [Length units](#311-length-units)
- **Quick Reference: Import Cheat Sheet** — [imports](#quick-reference-import-cheat-sheet)
- **Escape-hatch recipes** — [combo chart, overlapping conditional rules, rich text runs, KPI dashboard, section-scoped headers, VBA preserve](#escape-hatch-recipes)

Examples: [examples/office-documents.md](../examples/office-documents.md) · Cross-tool pipelines: [examples/data-pipelines.md](../examples/data-pipelines.md).

---

# 1. openpyxl (Excel .xlsx)

```python
from openpyxl import Workbook, load_workbook
```

## 1.1 Workbook & Worksheet Operations

> `claw xlsx new|read|append|meta` covers create / open / save / sheet CRUD — see [claw/xlsx.md](claw/xlsx.md). Below: API reference for the escape hatches (`read_only=True`, `data_only=True`, `keep_vba=True`, `keep_links=True`, `Workbook(write_only=True)` streaming, sheet tab colors, hidden / veryHidden sheet states).

`load_workbook` keyword args:

| Arg | Purpose |
|---|---|
| `read_only=True` | Streaming read for large files |
| `data_only=True` | Return cached formula values instead of formulas |
| `keep_vba=True` | Preserve VBA macros on round-trip (required for `.xlsm`) |
| `keep_links=True` | Preserve external workbook links |

`Workbook(write_only=True)` — streaming write; only `ws.append(...)` is available.

Sheet-state values: `"visible"` · `"hidden"` · `"veryHidden"` (can't be unhidden from Excel UI).

Tab color: `ws.sheet_properties.tabColor = "FF0000"` (hex RGB, no `#`).

## 1.2 Cell Operations

> `claw xlsx read|append` covers read / write / iterate / append — see [claw/xlsx.md](claw/xlsx.md). Below: data-type codes, merged-cell API, hyperlink + comment API the CLI doesn't wrap.

`cell.data_type` codes:

| Code | Meaning |
|---|---|
| `"s"` | string |
| `"n"` | number |
| `"d"` | date |
| `"b"` | bool |
| `"f"` | formula |
| `"e"` | error |

Range access: `ws["A1":"C3"]` tuple-of-tuples · `ws["A"]` whole column · `ws[1]` whole row · `ws.iter_rows(..., values_only=True|False)` · `ws.iter_cols(...)`.

Merged cells: `ws.merge_cells("A1:D1")` / `ws.unmerge_cells("A1:D1")` · read via `ws.merged_cells.ranges`.

Hyperlinks:

```python
from openpyxl.worksheet.hyperlink import Hyperlink
ws["A1"].hyperlink = Hyperlink(ref="A1", location="'Sheet2'!A1", display="Go to Sheet2")
ws["A1"].style = "Hyperlink"
```

Comments: `ws["A1"].comment = Comment("text", "Author")` · `.width` / `.height` in pixels.

## 1.3 Styling & Formatting

> `claw xlsx style|format` covers single-cell / range styling — see [claw/xlsx.md](claw/xlsx.md). Below: full `Font` / `PatternFill` / `GradientFill` / `Border` / `Alignment` / `NamedStyle` / `CellRichText` parameter surface.

```python
from openpyxl.styles import Font, PatternFill, GradientFill, Border, Side, Alignment, Protection, NamedStyle, numbers
from openpyxl.styles.colors import Color
```

### Font

| Param | Type / Values |
|---|---|
| `name` | Font family name (e.g. `"Calibri"`) |
| `size` | Point size (float) |
| `bold` / `italic` / `strike` | bool |
| `underline` | `"none"` / `"single"` / `"double"` / `"singleAccounting"` / `"doubleAccounting"` |
| `vertAlign` | `"superscript"` / `"subscript"` / `"baseline"` / `None` |
| `color` | 6-char hex RGB string, or `Color()` object |
| `family` | 1=Roman, 2=Swiss, 3=Modern, 4=Script, 5=Decorative |
| `scheme` | `"major"` / `"minor"` / `None` |

`Color()` forms: `Color(rgb="FF0000")` · `Color(theme=1)` (theme index 0-11) · `Color(indexed=8)` (0-63) · `Color(tint=-0.5)` (-1.0 to 1.0).

### PatternFill

`patternType` values (18): `"none"`, `"solid"`, `"darkDown"`, `"darkGray"`, `"darkGrid"`, `"darkHorizontal"`, `"darkTrellis"`, `"darkUp"`, `"darkVertical"`, `"gray0625"`, `"gray125"`, `"lightDown"`, `"lightGray"`, `"lightGrid"`, `"lightHorizontal"`, `"lightTrellis"`, `"lightUp"`, `"lightVertical"`, `"mediumGray"`.

### GradientFill

Params: `type="linear"|"path"`, `degree` (angle for linear), `left` / `right` / `top` / `bottom` (0.0-1.0 focal for path), `stop=[Color, ...]`.

### Border / Side

`Side.border_style` values (14): `None`, `"thin"`, `"medium"`, `"thick"`, `"double"`, `"hair"`, `"dotted"`, `"dashed"`, `"mediumDashed"`, `"dashDot"`, `"mediumDashDot"`, `"dashDotDot"`, `"mediumDashDotDot"`, `"slantDashDot"`.

`Border` accepts `left`, `right`, `top`, `bottom`, `diagonal` (each a `Side`) plus `diagonalDown` / `diagonalUp` bools.

### Alignment

| Param | Values |
|---|---|
| `horizontal` | `"general"` / `"left"` / `"center"` / `"right"` / `"fill"` / `"justify"` / `"centerContinuous"` / `"distributed"` |
| `vertical` | `"top"` / `"center"` / `"bottom"` / `"justify"` / `"distributed"` |
| `textRotation` | 0-180 (degrees); 255 = vertical stacked |
| `wrapText` / `shrinkToFit` / `justifyLastLine` | bool |
| `indent` / `relativeIndent` | int |
| `readingOrder` | 0=context, 1=LTR, 2=RTL |

### Number Formats

Common strings: `"0.00"`, `"#,##0"`, `"#,##0.00"`, `"0%"`, `"$#,##0.00"`, `"yyyy-mm-dd"`, `"hh:mm:ss"`, `"0.00E+00"`, `"@"` (force text), `"[Red]0.00;[Blue]-0.00"` (conditional colors).

Constants: `openpyxl.styles.numbers.FORMAT_PERCENTAGE`, `FORMAT_DATE_DATETIME`, `FORMAT_NUMBER_COMMA_SEPARATED1`, `FORMAT_CURRENCY_USD_SIMPLE`, etc.

### Named Styles

```python
style = NamedStyle(name="highlight")
style.font = Font(bold=True, size=14, color="FFFFFF")
style.fill = PatternFill(patternType="solid", fgColor="4472C4")
style.alignment = Alignment(horizontal="center")
style.number_format = "#,##0.00"
wb.add_named_style(style)
cell.style = "highlight"
```

### Rich Text (escape hatch — see recipe #3)

`CellRichText` + `TextBlock(InlineFont(...), "text")`. `InlineFont` fields: `rFont`, `charset`, `family`, `b`, `i`, `strike`, `outline`, `shadow`, `condense`, `extend`, `color`, `sz`, `u`, `vertAlign`, `scheme`.

## 1.4 Conditional Formatting

> Single-rule cases covered by `claw xlsx conditional` — see [claw/xlsx.md](claw/xlsx.md). Below: rule-class parameter surface. Overlapping stacks with `stopIfTrue` sequencing is escape-hatch — see recipe #2.

```python
from openpyxl.formatting.rule import CellIsRule, FormulaRule, ColorScaleRule, DataBarRule, IconSetRule
```

### CellIsRule

- `operator`: `"between"` / `"notBetween"` / `"equal"` / `"notEqual"` / `"greaterThan"` / `"lessThan"` / `"greaterThanOrEqual"` / `"lessThanOrEqual"`.
- `formula`: list of values (2 for between/notBetween, else 1).
- `fill` / `font` / `border`: openpyxl style objects.
- `stopIfTrue`: bool — halt rule stack when this rule matches.

### FormulaRule

- `formula`: list with one formula that returns `TRUE` / `FALSE`.
- `fill` / `font` / `border` / `stopIfTrue` as above.

### ColorScaleRule

2-color: `start_type` / `start_value` / `start_color` + `end_*`.
3-color: add `mid_type` / `mid_value` / `mid_color`.

`*_type` values: `"min"` / `"max"` / `"num"` / `"percent"` / `"percentile"` / `"formula"`.

### DataBarRule

Params: `start_type`, `start_value`, `end_type`, `end_value`, `color` (bar color), `showValue` (bool), `minLength` / `maxLength` (percent).

### IconSetRule

`icon_style` values: `"3Arrows"`, `"3ArrowsGray"`, `"3Flags"`, `"3Signs"`, `"3Stars"`, `"3Symbols"`, `"3Symbols2"`, `"3TrafficLights1"`, `"3TrafficLights2"`, `"3Triangles"`, `"4Arrows"`, `"4ArrowsGray"`, `"4Rating"`, `"4RedToBlack"`, `"4TrafficLights"`, `"5Arrows"`, `"5ArrowsGray"`, `"5Quarters"`, `"5Rating"`.

Other params: `type` (`"percent"` / `"num"` / `"percentile"` / `"formula"`), `values` (threshold list), `showValue`, `reverse`.

## 1.5 Data Validation

> `claw xlsx validate` covers list / range / text-length validations — see [claw/xlsx.md](claw/xlsx.md). Below: full `DataValidation` parameter surface.

| Param | Values / Purpose |
|---|---|
| `type` | `"whole"` / `"decimal"` / `"list"` / `"date"` / `"time"` / `"textLength"` / `"custom"` |
| `operator` | `"between"` / `"notBetween"` / `"equal"` / `"notEqual"` / `"greaterThan"` / `"lessThan"` / `"greaterThanOrEqual"` / `"lessThanOrEqual"` (not used for list / custom) |
| `formula1` | First value / formula / list string |
| `formula2` | Second value (for between / notBetween) |
| `allow_blank` | bool |
| `showDropDown` | bool — **`False` SHOWS** the dropdown (counterintuitive) |
| `showInputMessage` / `showErrorMessage` | bool |
| `errorTitle` / `error` | Error dialog text |
| `errorStyle` | `"stop"` / `"warning"` / `"information"` |
| `promptTitle` / `prompt` | Input hint text |

Apply with `dv.add("A1:A100")` then `ws.add_data_validation(dv)`.

## 1.6 Charts

> `claw xlsx chart` wraps single-plot bar / line / pie / scatter / doughnut / area — see [claw/xlsx.md](claw/xlsx.md). Combo charts, dual axes, trendlines, error bars, custom markers, per-series graphicalProperties stay in the library — see recipe #1.

```python
from openpyxl.chart import (
    AreaChart, AreaChart3D, BarChart, BarChart3D,
    LineChart, LineChart3D, PieChart, PieChart3D,
    DoughnutChart, ScatterChart, BubbleChart,
    RadarChart, StockChart, SurfaceChart, SurfaceChart3D,
    Reference, Series,
)
```

### Chart-type specific notes

| Class | Key properties |
|---|---|
| `AreaChart` / `AreaChart3D` | `grouping`: `"standard"` / `"stacked"` / `"percentStacked"` |
| `BarChart` / `BarChart3D` | `type="col"` (vertical) / `"bar"` (horizontal); `grouping`; `overlap` (-100..100); `gapWidth` (0-500) |
| `LineChart` / `LineChart3D` | `grouping` |
| `PieChart` / `PieChart3D` | No axes; single data series |
| `DoughnutChart` | `hole_size` 10-90 (default 50) |
| `ScatterChart` | `style`: `"line"` / `"lineMarker"` / `"marker"` / `"smooth"` / `"smoothMarker"` |
| `BubbleChart` | Each series needs x, y, size references |
| `RadarChart` | `type`: `"standard"` / `"filled"` / `"marker"` |
| `StockChart` | Requires 3-5 series (HLC, OHLC, Volume-*) |
| `SurfaceChart` / `SurfaceChart3D` | 3D surface |

Chart-wide props: `style` (1-48), `title`, `x_axis.title`, `y_axis.title`, `width` / `height` in cm.

### Axes

Numeric-axis props: `scaling.min` / `scaling.max` / `scaling.logBase` · `majorUnit` / `minorUnit` · `majorGridlines = None` to hide · `tickLblPos` (`"high"` / `"low"` / `"nextTo"` / `None`) · `numFmt` · `delete = True` to hide axis · `crosses` (`"min"` / `"max"` / `"autoZero"`) · `crossesAt`.

Text-axis props: `tickLblPos`, `lblOffset` (percent), `tickLblSkip` (every Nth), `tickMarkSkip`.

Date-axis: set `chart.x_axis = DateAxis()` then `baseTimeUnit` / `majorUnit` / `majorTimeUnit` in `"days"` / `"months"` / `"years"`.

### Legend

`chart.legend = Legend()` · `position` in `"b"` / `"t"` / `"l"` / `"r"` / `"tr"` · `chart.legend = None` removes it.

### Data labels

`chart.dataLabels = DataLabelList()` — bool flags: `showVal`, `showCatName`, `showSerName`, `showPercent`, `showLeaderLines`; plus `numFmt`.

### Series graphical properties

`series.graphicalProperties.solidFill` / `.line.solidFill` / `.line.width` (EMU) / `.line.dashStyle` (`"solid"` / `"dash"` / `"dot"` / `"dashDot"` / `"lgDash"`, ...).

Marker symbols (line/scatter): `"circle"` / `"dash"` / `"diamond"` / `"dot"` / `"plus"` / `"square"` / `"star"` / `"triangle"` / `"x"` / `"auto"`. Size 2-72.

### Trendlines

`series.trendline = Trendline(...)` — `trendlineType`: `"linear"` / `"log"` / `"exp"` / `"power"` / `"poly"` / `"movingAvg"`; `order` (2-6 for poly); `period` (movingAvg); `forward` / `backward`; `dispEq` / `dispRSqr` (bool); `intercept`.

### Error bars

`series.errBars = ErrorBars(errBarType="both"|"plus"|"minus", errValType="fixedVal"|"percentage"|"stdDev"|"stdErr"|"cust", val=N)`.

## 1.7 Tables

> `claw xlsx table` wraps creation + built-in styles — see [claw/xlsx.md](claw/xlsx.md). Below: built-in style names and `totalsRowCount` API.

Built-in table style names: `TableStyleLight1`–`TableStyleLight28` · `TableStyleMedium1`–`TableStyleMedium28` · `TableStyleDark1`–`TableStyleDark11`.

`TableStyleInfo` bool flags: `showFirstColumn`, `showLastColumn`, `showRowStripes`, `showColumnStripes`.

Totals row: `tab.totalsRowCount = 1` then configure per-column via table column objects.

## 1.8 Defined Names / Named Ranges

> `claw xlsx name add` covers workbook-scoped names — see [claw/xlsx.md](claw/xlsx.md). Below: sheet-scoped names.

```python
from openpyxl.workbook.defined_name import DefinedName
dn = DefinedName("LocalRange", attr_text="Sheet1!$A$1:$B$10", localSheetId=0)  # sheet-scoped
wb.defined_names.add(dn)
```

Read: `for name, dn in wb.defined_names.items(): ...` (openpyxl 3.1+ is a `DefinedNameDict`).

## 1.9 Auto-Filter & Sorting

> `claw xlsx filter` wraps auto-filter + sort — see [claw/xlsx.md](claw/xlsx.md).

Programmatic API: `ws.auto_filter.ref = "A1:D100"` · `ws.auto_filter.add_filter_column(0, ["Value1", "Value2"])` · `ws.auto_filter.add_sort_condition("B1:B100")`.

## 1.10 Images

> `claw xlsx image add` wraps image placement — see [claw/xlsx.md](claw/xlsx.md).

Library: `from openpyxl.drawing.image import Image` then `Image("logo.png")`, set `.width` / `.height` in pixels, `ws.add_image(img, "A1")`.

## 1.11 Page Setup & Print

> `claw xlsx print-setup` wraps orientation, paper, fit-to, margins, print-area, print-titles — see [claw/xlsx.md](claw/xlsx.md). Below: header-footer escape codes and page-break API.

Orientation: `"portrait"` / `"landscape"`.
Paper size constants: `ws.PAPERSIZE_LETTER`, `ws.PAPERSIZE_A4`, `ws.PAPERSIZE_A3`, etc.

Header-footer escape codes: `&P` page number · `&N` total pages · `&D` date · `&T` time · `&F` filename · `&A` sheet name.

Header-footer sections: `.oddHeader.{left,center,right}.text` / `.evenHeader.*` / `.firstHeader.*` (same for footer). Each section supports `.font`, `.size`, `.color`.

Page breaks:

```python
from openpyxl.worksheet.pagebreak import Break, RowBreak, ColBreak
ws.row_breaks.append(Break(id=20))     # horizontal break after row 20
ws.col_breaks.append(Break(id=5))      # vertical break after col 5
```

## 1.12 Worksheet Protection

> `claw xlsx protect` wraps sheet / workbook passwords and common bool flags — see [claw/xlsx.md](claw/xlsx.md). Below: full per-permission surface.

Granular bool permissions on `ws.protection`: `formatCells`, `formatColumns`, `formatRows`, `insertColumns`, `insertRows`, `insertHyperlinks`, `deleteColumns`, `deleteRows`, `sort`, `autoFilter`, `pivotTables`, `objects`, `scenarios`.

Cell-level: `cell.protection = Protection(locked=True, hidden=False)` — takes effect only when sheet protection is enabled.

## 1.13 Freeze Panes

> `claw xlsx freeze` wraps this — see [claw/xlsx.md](claw/xlsx.md).

Quick reference: `ws.freeze_panes = "B2"` freezes row 1 + col A · `"A2"` row 1 only · `"B1"` col A only · `None` unfreezes.

## 1.14 Column Width & Row Height

Escape-hatch — not wrapped by `claw`.

```python
ws.column_dimensions["A"].width = 25        # character-width units
ws.column_dimensions["A"].bestFit = True    # auto-fit hint only
ws.row_dimensions[1].height = 30            # points
ws.column_dimensions["C"].hidden = True
ws.row_dimensions[5].hidden = True
# Outline grouping
ws.column_dimensions.group("A", "D", outline_level=1, hidden=False)
ws.row_dimensions.group(1, 10, outline_level=1, hidden=False)
```

---

# 2. python-docx (Word .docx)

```python
from docx import Document
from docx.shared import Inches, Cm, Mm, Pt, Emu, Twips, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER, WD_UNDERLINE
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL, WD_ROW_HEIGHT_RULE
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
```

## 2.1 Document Operations

> `claw docx new|from-md` covers create / open / save — see [claw/docx.md](claw/docx.md).

API: `Document()` (default template) · `Document("template.docx")` (open / use as template) · `doc.save("out.docx")` · `doc.save(BytesIO())` for in-memory.

## 2.2 Paragraphs & Runs

> `claw docx add-paragraph` covers common text + style + alignment — see [claw/docx.md](claw/docx.md). Below: full paragraph-format and font-property surface (escape hatch for tabs, line-spacing rules, underline styles, theme colors, highlight indices).

### Paragraph format (`p.paragraph_format`)

| Property | Purpose |
|---|---|
| `alignment` | `WD_ALIGN_PARAGRAPH.{LEFT,CENTER,RIGHT,JUSTIFY,DISTRIBUTE}` |
| `left_indent` / `right_indent` / `first_line_indent` | `Inches(...)` (negative = hanging) |
| `space_before` / `space_after` | `Pt(...)` |
| `line_spacing` | `Pt(...)` exact, or float multiple (1.0, 1.5, 2.0) |
| `line_spacing_rule` | `WD_LINE_SPACING.{EXACTLY,AT_LEAST,MULTIPLE,SINGLE,DOUBLE,ONE_POINT_FIVE}` |
| `keep_together` / `keep_with_next` / `page_break_before` / `widow_control` | bool |

Tab stops: `pf.tab_stops.add_tab_stop(position, alignment, leader)`.

- `WD_TAB_ALIGNMENT`: `LEFT`, `CENTER`, `RIGHT`, `DECIMAL`, `BAR`, `CLEAR`, `END`, `NUM`.
- `WD_TAB_LEADER`: `SPACES`, `DOTS`, `DASHES`, `LINES`, `HEAVY`, `MIDDLE_DOT`.

### Run / Font (`run.font`)

Bool props: `bold`, `italic`, `strike`, `double_strike`, `subscript`, `superscript`, `all_caps`, `small_caps`, `shadow`, `outline`, `emboss`, `imprint`, `hidden`, `no_proof`, `math`.

`underline` — `True` / `False` / one of `WD_UNDERLINE`: `NONE`, `SINGLE`, `WORDS`, `DOUBLE`, `DOTTED`, `THICK`, `DASH`, `DOT_DASH`, `DOT_DOT_DASH`, `WAVY`, `DOTTED_HEAVY`, `DASH_HEAVY`, `DOT_DASH_HEAVY`, `DOT_DOT_DASH_HEAVY`, `WAVY_HEAVY` (14 types).

`font.color.rgb = RGBColor(0xFF, 0x00, 0x00)` or `font.color.theme_color = MSO_THEME_COLOR.ACCENT_1`.

- `MSO_THEME_COLOR`: `ACCENT_1`–`ACCENT_6`, `BACKGROUND_1`–`BACKGROUND_2`, `DARK_1`–`DARK_2`, `LIGHT_1`–`LIGHT_2`, `FOLLOWED_HYPERLINK`, `HYPERLINK`, `TEXT_1`–`TEXT_2`, `MIXED`.

`font.highlight_color = WD_COLOR_INDEX.YELLOW`.

- `WD_COLOR_INDEX`: `AUTO`, `BLACK`, `BLUE`, `BRIGHT_GREEN`, `DARK_BLUE`, `DARK_RED`, `DARK_YELLOW`, `GRAY_25`, `GRAY_50`, `GREEN`, `PINK`, `RED`, `TEAL`, `TURQUOISE`, `VIOLET`, `WHITE`, `YELLOW`.

## 2.3 Headings & Lists

> `claw docx add-heading` covers headings — see [claw/docx.md](claw/docx.md).

Library: `doc.add_heading("Title", level=0)` (title) through `level=9`.

Bullet / numbered list paragraph styles (from default template):

| Style | Effect |
|---|---|
| `List Bullet` / `List Bullet 2` / `List Bullet 3` | Bullet, indented levels |
| `List Number` / `List Number 2` / `List Number 3` | Numbered, indented levels |

Apply via `doc.add_paragraph("text", style="List Bullet")`.

## 2.4 Tables

> `claw docx add-table | table fit` covers creation / sizing / autofit / style — see [claw/docx.md](claw/docx.md). Below: built-in style names and XML-level borders / shading escape hatch.

Built-in table styles: `"Table Grid"`, `"Light List"`, `"Light Grid"`, `"Medium Shading 1"`, `"Light Shading - Accent 1"`, `"Colorful Grid - Accent 2"`, ... (see Word's Table Design gallery for the full list).

Alignment: `table.alignment = WD_TABLE_ALIGNMENT.{LEFT,CENTER,RIGHT}`.

Row height rule: `row.height_rule = WD_ROW_HEIGHT_RULE.{EXACTLY,AT_LEAST,AUTO}`.

Cell vertical alignment: `cell.vertical_alignment = WD_ALIGN_VERTICAL.{TOP,CENTER,BOTTOM}`.

Merge: `cell_a.merge(cell_b)` — works for horizontal or vertical merges (pass opposite-corner cells).

Borders / shading require direct XML — `claw` doesn't wrap the OOXML level:

```python
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="4472C4"/>')
cell._tc.get_or_add_tcPr().append(shading)
tc_pr = cell._tc.get_or_add_tcPr()
borders = parse_xml(
    f'<w:tcBorders {nsdecls("w")}>'
    '  <w:top w:val="single" w:sz="12" w:color="000000"/>'
    '  <w:bottom w:val="single" w:sz="12" w:color="000000"/>'
    '  <w:left w:val="single" w:sz="12" w:color="000000"/>'
    '  <w:right w:val="single" w:sz="12" w:color="000000"/>'
    '</w:tcBorders>'
)
tc_pr.append(borders)
# w:val types: "single","double","dotted","dashed","thick","thinThickSmallGap", ...
# w:sz = border width in 1/8 pt (12 = 1.5pt)
```

## 2.5 Images

> `claw docx add-image` covers inline images — see [claw/docx.md](claw/docx.md).

Library: `doc.add_picture(path_or_stream, width=Inches(4), height=Inches(3))` — specify one of width/height to preserve aspect; specifying both may distort.

## 2.6 Sections & Page Layout

> `claw docx section add` covers section breaks + page size + orientation + margins — see [claw/docx.md](claw/docx.md). Below: enum listings.

- `WD_SECTION`: `NEW_PAGE`, `CONTINUOUS`, `EVEN_PAGE`, `ODD_PAGE`, `NEW_COLUMN`.
- `WD_ORIENT`: `PORTRAIT`, `LANDSCAPE`. When toggling, also swap `page_width` / `page_height`.

Section props: `page_width`, `page_height`, `orientation`, `top_margin`, `bottom_margin`, `left_margin`, `right_margin`, `gutter`, `header_distance`, `footer_distance` — all accept length units (Inches/Cm/Mm/Pt/Emu/Twips).

## 2.7 Headers & Footers

> `claw docx header set | footer set` covers basic text / alignment — see [claw/docx.md](claw/docx.md). Below: section linking model, different-first-page + even/odd, escape-hatch recipe #5 for section-scoped headers.

Linking model: `header.is_linked_to_previous = True/False` — when `True`, the header inherits from the previous section.

Different first page: `section.different_first_page_header_footer = True` then use `section.first_page_header` / `section.first_page_footer`.

Even/odd pages (document-level toggle): `doc.settings.odd_and_even_pages_header_footer = True` then `section.even_page_header` / `section.even_page_footer`.

Headers / footers support full body content — paragraphs, tables (via `header.add_table(rows, cols, width)`), and images (via `run.add_picture(path, width=...)`).

## 2.8 Breaks

> `claw docx insert pagebreak` covers page breaks — see [claw/docx.md](claw/docx.md). Below: break-type enum.

- `WD_BREAK`: `LINE`, `PAGE`, `COLUMN`, `LINE_CLEAR_LEFT`, `LINE_CLEAR_RIGHT`, `LINE_CLEAR_ALL`.

API: `doc.add_page_break()` or `run.add_break(WD_BREAK.COLUMN)` for other break types.

## 2.9 Hyperlinks

> `claw docx hyperlink add` covers the common "link a run of text" case — see [claw/docx.md](claw/docx.md). python-docx has **no built-in hyperlink API**; `claw` uses (and exposes) the same XML helper below.

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import docx.opc.constants

def add_hyperlink(paragraph, url, text, color="0563C1", underline=True):
    part = paragraph.part
    r_id = part.relate_to(url, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    if color:
        c = OxmlElement("w:color"); c.set(qn("w:val"), color); rPr.append(c)
    if underline:
        u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rPr.append(u)
    new_run.append(rPr)
    new_run.text = text
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink
```

## 2.10 Styles

> `claw docx style define | apply` covers common create / modify — see [claw/docx.md](claw/docx.md). Below: enum listing.

- `WD_STYLE_TYPE`: `PARAGRAPH`, `CHARACTER`, `TABLE`, `LIST`.

New style pattern: `styles.add_style("Name", WD_STYLE_TYPE.PARAGRAPH)` then set `base_style = styles["Heading 1"]`, `font.*`, `paragraph_format.*`.

## 2.11 Core Properties

> `claw docx meta get | set` covers read / write — see [claw/docx.md](claw/docx.md).

`doc.core_properties`: `author`, `title`, `subject`, `keywords`, `comments`, `category`, `content_status` (`"Draft"` / `"Final"` / custom), `created` (datetime, read-only), `modified` (datetime), `last_modified_by`, `revision` (int), `version`, `language`, `identifier`.

## 2.12 Length Units

```python
from docx.shared import Inches, Cm, Mm, Pt, Emu, Twips
Inches(1)       # = 914400 EMU
Cm(2.54)        # = 914400 EMU
Mm(25.4)        # = 914400 EMU
Pt(72)          # = 914400 EMU
Emu(914400)     # = 1 inch
Twips(1440)     # = 914400 EMU (1 inch = 1440 twips)
```

All return EMU-compatible `Length` objects usable for any dimension property.

---

# 3. python-pptx (PowerPoint .pptx)

```python
from pptx import Presentation
from pptx.util import Inches, Cm, Mm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
```

## 3.1 Presentation & Slides

> `claw pptx new | add-slide | from-outline` covers create / layouts / add-slide / notes / save — see [claw/pptx.md](claw/pptx.md).

Slide dimensions presets:

| Aspect | Width × Height |
|---|---|
| Widescreen 16:9 | `Inches(13.333)` × `Inches(7.5)` |
| Standard 4:3 | `Inches(10)` × `Inches(7.5)` |

Default slide layouts by index:

| Idx | Layout |
|---|---|
| 0 | Title Slide |
| 1 | Title and Content |
| 2 | Section Header |
| 3 | Two Content |
| 4 | Comparison |
| 5 | Title Only |
| 6 | Blank |
| 7 | Content with Caption |
| 8 | Picture with Caption |

Notes: `slide.notes_slide.notes_text_frame.text = "..."`.

## 3.2 Shapes

> `claw pptx add-shape | add-image | add-table` covers the common shape-inserts — see [claw/pptx.md](claw/pptx.md). Below: enum catalog and escape-hatch APIs (freeform, connector, group, picture crop).

### Common shape properties

`shape.left / .top / .width / .height` (Length) · `rotation` (degrees CW) · `name` · `shape_id` (read-only) · `shape_type` (MSO_SHAPE_TYPE).

### `MSO_SHAPE` — 187 presets (AutoShape catalog)

Common: `RECTANGLE`, `ROUNDED_RECTANGLE`, `OVAL`, `DIAMOND`, `TRIANGLE`, `RIGHT_TRIANGLE`, `PARALLELOGRAM`, `TRAPEZOID`, `PENTAGON`, `HEXAGON`, `OCTAGON`, `CROSS`.

Stars / decorative: `STAR_4_POINT`, `STAR_5_POINT`, `STAR_6_POINT`, `HEART`, `LIGHTNING_BOLT`, `SUN`, `MOON`, `CLOUD`.

Arrows: `LEFT_ARROW`, `RIGHT_ARROW`, `UP_ARROW`, `DOWN_ARROW`, `LEFT_RIGHT_ARROW`, `UP_DOWN_ARROW`, `CURVED_RIGHT_ARROW`, `CHEVRON`.

Callouts: `CALLOUT_1`, `CALLOUT_2`, `CALLOUT_3`, `ROUNDED_RECTANGLE_CALLOUT`, `OVAL_CALLOUT`, `CLOUD_CALLOUT`.

Flowchart: `FLOWCHART_PROCESS`, `FLOWCHART_DECISION`, `FLOWCHART_DATA`, `FLOWCHART_TERMINATOR`, `FLOWCHART_DOCUMENT`, …

### Picture crop

```python
pic.crop_left = 0.1     # proportional 0.0-1.0
pic.crop_right = 0.1
pic.crop_top = 0.05
pic.crop_bottom = 0.05
```

### Table props (on `table_shape.table`)

Banding flags: `first_row`, `last_row`, `first_col`, `last_col`, `horz_banding`, `vert_banding`.
Cell props: `fill.solid()` + `fill.fore_color.rgb`, `vertical_anchor = MSO_ANCHOR.{TOP,MIDDLE,BOTTOM}`, `margin_{left,right,top,bottom}`.

### Connector (escape hatch)

```python
connector = slide.shapes.add_connector(
    connector_type=1,              # 1=straight, 2=elbow, 3=curved
    begin_x=Inches(1), begin_y=Inches(1),
    end_x=Inches(5), end_y=Inches(3),
)
connector.begin_connect(shape1, 0)    # shape + connection point index
connector.end_connect(shape2, 2)
```

### Freeform (escape hatch)

```python
builder = slide.shapes.build_freeform(start_x=Inches(1), start_y=Inches(1))
builder.add_line_segments([(Inches(3), Inches(1)), (Inches(3), Inches(3)), (Inches(1), Inches(3))])
builder.close()
freeform = builder.convert_to_shape()
```

### Group shape (escape hatch)

`slide.shapes.add_group_shape()` — `group.shapes` exposes the `GroupShapes` collection; complex groups require XML-level manipulation via `_spTree`.

## 3.3 Text Frames & Formatting

> `claw pptx fill` covers basic text insertion + alignment — see [claw/pptx.md](claw/pptx.md). Below: full paragraph / run property surface.

TextFrame props: `text`, `word_wrap` (bool), `auto_size` (`MSO_AUTO_SIZE.{NONE, SHAPE_TO_FIT_TEXT, TEXT_TO_FIT_SHAPE}`), `margin_{left,right,top,bottom}`.

Paragraph alignment: `PP_ALIGN.{LEFT,CENTER,RIGHT,JUSTIFY,DISTRIBUTE,JUSTIFY_LOW,THAI_DISTRIBUTE}`.

Paragraph props: `level` (0-8 indent), `space_before` / `space_after` (Pt or Emu), `line_spacing` (Pt exact or float multiple), `font`.

Run props (same for paragraph.font and run.font): `name`, `size` (Pt), `bold`, `italic`, `underline` (True/False/None + additional XML-level types `"sng"`, `"dbl"`, `"heavy"`, `"dotted"`, `"dash"`, `"dashHeavy"`, ...), `color.rgb = RGBColor(r, g, b)`, `color.theme_color = MSO_THEME_COLOR.*`, `color.brightness` (-1.0 to 1.0 for theme colors).

Hyperlinks: `run.hyperlink.address = "https://..."`.

## 3.4 Charts

> `claw pptx add-chart | chart refresh` covers common chart types + data binding — see [claw/pptx.md](claw/pptx.md). Below: XL_CHART_TYPE catalog, XY/bubble data models, axis / legend / data-label enums.

```python
from pptx.chart.data import CategoryChartData, XyChartData, BubbleChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_MARK, XL_TICK_LABEL_POSITION
```

### XL_CHART_TYPE catalog

- **Bar / Column**: `BAR_CLUSTERED` / `BAR_STACKED` / `BAR_STACKED_100`, `COLUMN_CLUSTERED` / `COLUMN_STACKED` / `COLUMN_STACKED_100`, plus `THREE_D_*` variants.
- **Line**: `LINE`, `LINE_MARKERS`, `LINE_MARKERS_STACKED`, `LINE_MARKERS_STACKED_100`, `LINE_STACKED`, `LINE_STACKED_100`, `THREE_D_LINE`.
- **Pie / Doughnut**: `PIE`, `PIE_EXPLODED`, `THREE_D_PIE`, `THREE_D_PIE_EXPLODED`, `DOUGHNUT`, `DOUGHNUT_EXPLODED`.
- **Area**: `AREA`, `AREA_STACKED`, `AREA_STACKED_100`, plus `THREE_D_*` variants.
- **Scatter / XY**: `XY_SCATTER`, `XY_SCATTER_LINES`, `XY_SCATTER_LINES_NO_MARKERS`, `XY_SCATTER_SMOOTH`, `XY_SCATTER_SMOOTH_NO_MARKERS`.
- **Bubble**: `BUBBLE`, `BUBBLE_THREE_D_EFFECT`.
- **Radar**: `RADAR`, `RADAR_FILLED`, `RADAR_MARKERS`.

### XY / Bubble data

```python
xy = XyChartData(); s = xy.add_series("S1"); s.add_data_point(1.0, 2.5)
bub = BubbleChartData(); s = bub.add_series("S1"); s.add_data_point(1.0, 2.5, 10)   # x, y, size
```

### Legend / axes / labels

- `XL_LEGEND_POSITION`: `BOTTOM`, `CORNER`, `CUSTOM`, `LEFT`, `RIGHT`, `TOP`.
- `XL_TICK_MARK`: `CROSS`, `INSIDE`, `OUTSIDE`, `NONE`.
- `XL_TICK_LABEL_POSITION`: `HIGH`, `LOW`, `NEXT_TO_AXIS`, `NONE`.
- `XL_LABEL_POSITION`: `ABOVE`, `BELOW`, `BEST_FIT`, `CENTER`, `INSIDE_BASE`, `INSIDE_END`, `LEFT`, `MIXED`, `OUTSIDE_END`, `RIGHT`.

Value-axis props: `minimum_scale`, `maximum_scale`, `major_unit`, `minor_unit`, `has_major_gridlines`, `has_minor_gridlines`, `major_tick_mark`, `minor_tick_mark`, `tick_label_position`, `visible`.

Category-axis props: `has_title`, `axis_title.text_frame.text`, `tick_labels.font.size`, `tick_labels.number_format`, `tick_labels.number_format_is_linked`.

Data-label bool flags (`plot.data_labels.*`): `show_category_name`, `show_legend_key`, `show_percentage`, `show_series_name`, `show_value`; plus `number_format`, `label_position`.

Bar / column plot: `plot.gap_width` (0-500), `plot.overlap` (-100..100).

## 3.5 Fill & Line Formatting

> `claw pptx brand` covers solid fills + common theme tints — see [claw/pptx.md](claw/pptx.md). Gradients, pattern fills, picture fills, alpha blending stay in the library. Below: enum listings + gradient API.

### FillFormat

- `fill.solid()` + `fill.fore_color.rgb = RGBColor(...)` / `fill.fore_color.theme_color = MSO_THEME_COLOR.ACCENT_1` / `fill.fore_color.brightness = 0.4`.
- `fill.gradient()` + `fill.gradient_angle = 45` + `fill.gradient_stops[i].color.rgb = RGBColor(...)` + `.position = 0.0..1.0`.
- `fill.patterned()` + `fill.pattern = MSO_PATTERN.*` + `fill.fore_color.rgb` + `fill.back_color.rgb`.
- `fill.picture()` — image set via XML-level manipulation.
- `fill.background()` — transparent / no fill.
- Alpha via XML: `shape.fill._fill` element.

### LineFormat

- `shape.line.color.rgb = RGBColor(...)` / `.theme_color`.
- `shape.line.width = Pt(2.0)`.
- `shape.line.fill.background()` → no line · `shape.line.fill.solid()` → solid.
- `shape.line.dash_style = MSO_LINE_DASH_STYLE.*`.

`MSO_LINE_DASH_STYLE`: `SOLID`, `ROUND_DOT`, `SQUARE_DOT`, `DASH`, `DASH_DOT`, `LONG_DASH`, `LONG_DASH_DOT`, `LONG_DASH_DOT_DOT`, `DASH_STYLE_MIXED`, `SYSTEM_DASH`, `SYSTEM_DOT`, `SYSTEM_DASH_DOT`.

## 3.6 Placeholders

> `claw pptx fill --placeholder` covers common placeholder population — see [claw/pptx.md](claw/pptx.md).

`MSO_PLACEHOLDER` types: `TITLE` (0), `BODY` (1/13), `CENTER_TITLE` (3), `SUBTITLE` (4), `DATE` (10), `SLIDE_NUMBER` (12), `FOOTER` (11), `OBJECT` (7), `TABLE` (12), `CHART` (13), `ORG_CHART` (14), `MEDIA_CLIP` (16), `PICTURE` (18), `BITMAP` (9), `VERTICAL_BODY` (14), `VERTICAL_OBJECT` (15), `VERTICAL_TITLE` (16).

Picture placeholder: `pic_ph.insert_picture("image.png")` (placeholder must be a picture type).

## 3.7 Slide Background

Escape hatch — not wrapped.

```python
fill = slide.background.fill
fill.solid(); fill.fore_color.rgb = RGBColor(0xF0, 0xF0, 0xF0)
# Or gradient:
fill.gradient()
fill.gradient_stops[0].color.rgb = RGBColor(0x00, 0x00, 0x80)
fill.gradient_stops[1].color.rgb = RGBColor(0x00, 0x00, 0x00)
```

## 3.8 Hyperlinks & Click Actions

> `claw pptx link add` covers run-level + shape click-action hyperlinks — see [claw/pptx.md](claw/pptx.md).

Library: `run.hyperlink.address = "https://example.com"` · `shape.click_action.hyperlink.address = "..."` · `shape.click_action.target_slide = prs.slides[2]` (internal link).

## 3.9 OLE Embedding & Media

Escape hatch — python-pptx has limited native media support. Use `slide.shapes._spTree` + `pptx.oxml` helpers via `lxml` for embedded video / audio / OLE objects. `claw` does **not** wrap this surface.

## 3.10 Core Properties

> `claw pptx meta` covers read / write — see [claw/pptx.md](claw/pptx.md).

`prs.core_properties`: `author`, `title`, `subject`, `keywords`, `comments`, `category`, `content_status`, `last_modified_by`, `revision` (int), `created` (datetime), `modified` (datetime).

## 3.11 Length Units

```python
from pptx.util import Inches, Cm, Mm, Pt, Emu
Inches(1)       # = 914400 EMU
Cm(2.54)        # = 914400 EMU
Mm(25.4)        # = 914400 EMU
Pt(72)          # = 914400 EMU
Emu(914400)     # Direct EMU value
```

---

# Quick Reference: Import Cheat Sheet

```python
# ---- openpyxl ----
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, GradientFill, Border, Side, Alignment, Protection, NamedStyle
from openpyxl.styles.colors import Color
from openpyxl.styles.numbers import FORMAT_PERCENTAGE, FORMAT_NUMBER_COMMA_SEPARATED1
from openpyxl.formatting.rule import CellIsRule, FormulaRule, ColorScaleRule, DataBarRule, IconSetRule
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.worksheet.pagebreak import Break
from openpyxl.chart import BarChart, LineChart, PieChart, ScatterChart, AreaChart, Reference, Series
from openpyxl.chart.axis import DateAxis, NumericAxis
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.trendline import Trendline
from openpyxl.chart.legend import Legend
from openpyxl.drawing.image import Image
from openpyxl.comments import Comment
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.workbook.defined_name import DefinedName

# ---- python-docx ----
from docx import Document
from docx.shared import Inches, Cm, Mm, Pt, Emu, Twips, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK, WD_UNDERLINE, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL, WD_ROW_HEIGHT_RULE
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.dml import MSO_THEME_COLOR
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement

# ---- python-pptx ----
from pptx import Presentation
from pptx.util import Inches, Cm, Mm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_MARK, XL_TICK_LABEL_POSITION
from pptx.enum.dml import MSO_THEME_COLOR, MSO_LINE_DASH_STYLE, MSO_PATTERN
from pptx.chart.data import CategoryChartData, XyChartData, BubbleChartData
```

---

## Escape-hatch recipes

Six patterns `claw` deliberately doesn't wrap. Use the library APIs directly.

### 1. Combo chart (bar + line on dual axis)

`claw xlsx chart` picks one series shape. Multi-plot combo charts require merging charts directly:

```python
from openpyxl.chart import BarChart, LineChart, Reference
bar = BarChart(); bar.add_data(Reference(ws, min_col=2, max_col=2, min_row=1, max_row=13),
                                titles_from_data=True)
bar.set_categories(Reference(ws, min_col=1, min_row=2, max_row=13))
bar.y_axis.title = "Revenue"

line = LineChart(); line.add_data(Reference(ws, min_col=3, max_col=3, min_row=1, max_row=13),
                                  titles_from_data=True)
line.y_axis.axId = 200           # unique ID for secondary axis
line.y_axis.crosses = "max"      # put it on the right
line.y_axis.title = "Margin %"

bar += line                      # combine
ws.add_chart(bar, "E2")
```

### 2. Overlapping conditional-formatting rules with `stopIfTrue`

`claw xlsx conditional` adds one rule at a time. Stacks where order matters (e.g. "red if <0, then yellow if <10 else green") need explicit `stopIfTrue` sequencing:

```python
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import PatternFill, Font

rng = "C2:C200"
ws.conditional_formatting.add(rng, CellIsRule(
    operator="lessThan", formula=["0"],
    fill=PatternFill(bgColor="FFC7CE"), font=Font(color="9C0006"),
    stopIfTrue=True,            # negatives stop here; next rules don't run
))
ws.conditional_formatting.add(rng, CellIsRule(
    operator="lessThan", formula=["10"],
    fill=PatternFill(bgColor="FFEB9C"), stopIfTrue=True,
))
ws.conditional_formatting.add(rng, CellIsRule(
    operator="greaterThanOrEqual", formula=["10"],
    fill=PatternFill(bgColor="C6EFCE"), font=Font(color="006100"),
))
```

### 3. Rich text runs in a single cell

`claw xlsx richtext set` accepts a JSON run list, which works until you need `rFont` / `vertAlign` / `scheme` overrides. Raw:

```python
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
rt = CellRichText(
    "Result: ",
    TextBlock(InlineFont(b=True, sz=14, color="006100"), "OK"),
    "  (",
    TextBlock(InlineFont(vertAlign="superscript", color="9C0006"), "2"),
    " errors)",
)
ws["A1"].value = rt
```

### 4. python-pptx KPI dashboard — per-shape positioning DSL

`claw pptx add-shape` wraps one shape per call. A 6-KPI grid is cleaner authored directly:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

prs = Presentation("brand.pptx")
slide = prs.slides.add_slide(prs.slide_layouts[6])   # Blank
kpis = [("Revenue", "$4.2M"), ("Churn", "1.1%"), ("NPS", "68"),
        ("ARR", "$52M"), ("CAC", "$280"), ("LTV", "$4.3k")]
for i, (label, value) in enumerate(kpis):
    col, row = i % 3, i // 3
    tile = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.4 + col * 4.3), Inches(1.2 + row * 2.6),
        Inches(4.0), Inches(2.2))
    tile.fill.solid(); tile.fill.fore_color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    tile.line.fill.background()
    tf = tile.text_frame; tf.word_wrap = True
    tf.paragraphs[0].text = label
    tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = RGBColor(0xB5, 0xC9, 0xE3)
    p = tf.add_paragraph(); p.text = value
    p.font.size = Pt(40); p.font.bold = True; p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
prs.save("kpi-dashboard.pptx")
```

### 5. Section-scoped header + page-numbered footer (python-docx)

`claw docx header set` defaults to all sections. Different headers per section need `is_linked_to_previous = False` on each after the first:

```python
from docx import Document
doc = Document("report.docx")
for i, section in enumerate(doc.sections):
    header = section.header
    header.is_linked_to_previous = (i == 0)      # first inherits; rest independent
    header.paragraphs[0].text = f"Part {i+1} — Confidential"
    footer = section.footer
    footer.is_linked_to_previous = (i == 0)
```

### 6. VBA-preserving round-trip

```python
wb = load_workbook("macro.xlsm", keep_vba=True)
# mutate sheets as usual; save as .xlsm to preserve macros
wb.save("updated.xlsm")
```
