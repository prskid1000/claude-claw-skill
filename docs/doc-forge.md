# Doc Forge — Document Creation Recipes

> Create Excel, Word, PowerPoint, and PDF documents with Python. Style them, add charts, upload to Drive.

**Related:** [workspace.md](workspace.md) | [pipelines.md](pipelines.md) | [mailbox.md](mailbox.md)

---

## Workflow

```
Create locally (Python) → Save to /tmp/ → Upload via gws drive files create --upload
```

## Excel — openpyxl

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, PieChart, LineChart, Reference
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule, DataBarRule

wb = Workbook()
ws = wb.active
ws.title = "Report"

# --- Styled headers ---
headers = ["Name", "Status", "Value", "Date"]
hdr_font = Font(bold=True, color="FFFFFF", size=12)
hdr_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
border = Border(*(Side(style='thin') for _ in range(4)))

for col, h in enumerate(headers, 1):
    c = ws.cell(row=1, column=col, value=h)
    c.font, c.fill, c.alignment, c.border = hdr_font, hdr_fill, Alignment(horizontal='center'), border

# --- Data ---
data = [["Item A", "Done", 1200, "2026-03-25"], ["Item B", "Pending", 800, "2026-03-26"]]
for ri, row in enumerate(data, 2):
    for ci, val in enumerate(row, 1):
        c = ws.cell(row=ri, column=ci, value=val)
        c.border = border

# --- Column widths, freeze, filter ---
for col in range(1, len(headers) + 1):
    ws.column_dimensions[get_column_letter(col)].width = 18
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(data)+1}"

# --- Charts ---
vals = Reference(ws, min_col=3, min_row=1, max_row=len(data)+1)
cats = Reference(ws, min_col=1, min_row=2, max_row=len(data)+1)

for ChartType, pos in [(BarChart, "F2"), (PieChart, "F18"), (LineChart, "P2")]:
    chart = ChartType()
    chart.add_data(vals, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, pos)

# --- Conditional formatting ---
ws.conditional_formatting.add(f"B2:B{len(data)+1}",
    CellIsRule(operator='equal', formula=['"Done"'], fill=PatternFill(bgColor="C6EFCE")))
ws.conditional_formatting.add(f"C2:C{len(data)+1}",
    DataBarRule(start_type='min', end_type='max', color="4472C4"))

# --- Number format, hyperlink, merged cells ---
ws['C2'].number_format = '#,##0.00'
ws['D2'].number_format = 'YYYY-MM-DD'
ws['A2'].hyperlink = "https://example.com"

# --- Multiple sheets, formulas ---
ws2 = wb.create_sheet("Summary")
ws2["A1"], ws2["B1"] = "Total", f"=SUM(Report!C2:C{len(data)+1})"
ws2.merge_cells('A3:C3')

# --- Print setup ---
ws.print_title_rows = '1:1'
ws.page_setup.orientation = 'landscape'

wb.save('/tmp/report.xlsx')
```

### Reading Excel

```python
wb = load_workbook('/tmp/report.xlsx', data_only=True)
for row in wb.active.iter_rows(min_row=2, values_only=True):
    print(row)
```

## Word — python-docx

```python
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = Document()

# --- Default font ---
doc.styles['Normal'].font.name = 'Calibri'
doc.styles['Normal'].font.size = Pt(11)

# --- Title + subtitle ---
doc.add_heading('Report Title', level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Generated: 2026-03-25')
run.font.size, run.font.color.rgb = Pt(10), RGBColor(128, 128, 128)

# --- Sections ---
doc.add_heading('Section 1: Overview', level=1)
doc.add_paragraph('Body text here.')

# --- Lists ---
doc.add_paragraph('Bullet point', style='List Bullet')
doc.add_paragraph('Step one', style='List Number')

# --- Inline formatting ---
p = doc.add_paragraph()
p.add_run('Bold').bold = True
p.add_run(' / ')
p.add_run('Italic').italic = True

# --- Table ---
table = doc.add_table(rows=3, cols=3, style='Table Grid')
table.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, h in enumerate(['Col A', 'Col B', 'Col C']):
    cell = table.rows[0].cells[i]
    cell.text = h
    cell.paragraphs[0].runs[0].font.bold = True

# --- Image ---
# doc.add_picture('/path/to/image.png', width=Inches(4))

# --- Page break + margins ---
doc.add_page_break()
section = doc.sections[0]
section.top_margin = section.bottom_margin = Cm(2)
section.left_margin = section.right_margin = Cm(2.5)

# --- Header / footer ---
section.header.paragraphs[0].text = "Company — Confidential"

doc.save('/tmp/report.docx')
```

## PowerPoint — python-pptx

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)  # 16:9

# --- Title slide ---
s = prs.slides.add_slide(prs.slide_layouts[0])
s.shapes.title.text = "Presentation Title"
s.placeholders[1].text = "Subtitle — Date"

# --- Bullet slide ---
s = prs.slides.add_slide(prs.slide_layouts[1])
s.shapes.title.text = "Key Points"
tf = s.placeholders[1].text_frame
tf.text = "First point"
p = tf.add_paragraph(); p.text = "Sub-point"; p.level = 1

# --- Custom text box ---
s = prs.slides.add_slide(prs.slide_layouts[6])
tx = s.shapes.add_textbox(Inches(1), Inches(1), Inches(5), Inches(1))
tx.text_frame.text = "Custom text"
tx.text_frame.paragraphs[0].font.size = Pt(24)

# --- Table ---
shape = s.shapes.add_table(4, 3, Inches(1), Inches(3), Inches(8), Inches(3))
for i, h in enumerate(["Metric", "Q1", "Q2"]):
    shape.table.cell(0, i).text = h

# --- Chart slide ---
s = prs.slides.add_slide(prs.slide_layouts[6])
cd = CategoryChartData()
cd.categories = ['Jan', 'Feb', 'Mar']
cd.add_series('Revenue', (100, 150, 200))
cd.add_series('Cost', (80, 120, 160))
s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(1), Inches(1), Inches(10), Inches(5.5), cd)

# --- Speaker notes ---
s.notes_slide.notes_text_frame.text = "Notes here"

prs.save('/tmp/presentation.pptx')
```

## PDF — reportlab (generate from scratch)

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

doc = SimpleDocTemplate("/tmp/report.pdf", pagesize=A4,
    topMargin=2*cm, bottomMargin=2*cm, leftMargin=2.5*cm, rightMargin=2.5*cm)
styles = getSampleStyleSheet()
story = []

title = ParagraphStyle('T', parent=styles['Title'], fontSize=28, textColor=HexColor('#1a237e'))
heading = ParagraphStyle('H', parent=styles['Heading1'], fontSize=16, textColor=HexColor('#283593'))
body = ParagraphStyle('B', parent=styles['Normal'], fontSize=11, leading=16)

story += [Paragraph("Report Title", title), Spacer(1, 30)]
story += [Paragraph("1. Overview", heading), Paragraph("Content...", body)]

data = [['Name', 'Status', 'Value'], ['A', 'Done', '$1,200'], ['B', 'Pending', '$800']]
t = Table(data, colWidths=[200, 120, 100])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), HexColor('#1a237e')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.white]),
]))
story += [t, PageBreak()]
doc.build(story)
```

## PDF — pymupdf (read, edit, screenshot, merge)

```python
import fitz

# Read text
doc = fitz.open("input.pdf")
for page in doc: print(page.get_text())

# Extract tables → pandas
for page in doc:
    for tab in page.find_tables(): df = tab.to_pandas()

# Merge PDFs
result = fitz.open()
for p in ["a.pdf", "b.pdf"]: result.insert_pdf(fitz.open(p))
result.save("merged.pdf")

# Watermark
for page in doc:
    page.insert_text((100, 100), "CONFIDENTIAL", fontsize=40, color=(0.8, 0, 0), rotate=45)

# Page → image (screenshot)
pix = doc[0].get_pixmap(matrix=fitz.Matrix(3, 3))
pix.save("screenshot.png")

# Extract images
for page in doc:
    for img in page.get_images():
        fitz.Pixmap(doc, img[0]).save(f"img_{img[0]}.png")
```

## PDF — pdfplumber (extract tables/text)

```python
import pdfplumber
with pdfplumber.open("invoice.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables()
        # Crop region
        cropped = page.within_bbox((0, 0, page.width/2, page.height/2))
```

## Conversions Not Covered Above

```bash
# Word → PDF
pandoc input.docx -o output.pdf

# Markdown → Word / PDF / PPT
pandoc input.md -o output.docx
pandoc input.md -o output.pdf --toc
pandoc input.md -o output.pptx
```

See [media-kit.md](media-kit.md) for Pandoc and [pipelines.md](pipelines.md) for full conversion flows.
