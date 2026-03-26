# Create Documents — Excel / Word / PowerPoint / PDF

> Create Excel, Word, PowerPoint, and PDF documents with Python. Style them, add charts, upload to Drive.

**Related:** [gws-quickref.md](gws-quickref.md) | [data-pipelines.md](data-pipelines.md) | [email-workflows.md](email-workflows.md)

---

## Workflow

```
Create locally (Python) → Save to /tmp/ → Upload via gws drive files create --upload
```

## Excel (minimal)

Use Excel when you need tables + light styling (and optionally charts).

```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "Report"
ws.append(["Col A", "Col B", "Col C"])
ws.append([1, 2, 3])
wb.save("/tmp/report.xlsx")
```

## Word (minimal)

Use Word when you need narrative text + a few tables.

```python
from docx import Document

doc = Document()
doc.add_heading("Report", level=0)
doc.add_paragraph("Summary goes here.")
doc.save("/tmp/report.docx")
```

## PowerPoint (minimal)

Use PowerPoint when you need a simple deck (title + bullets).

```python
from pptx import Presentation

prs = Presentation()
s = prs.slides.add_slide(prs.slide_layouts[0])
s.shapes.title.text = "Title"
prs.save("/tmp/deck.pptx")
```

## PDF (minimal)

- **Generate**: use `reportlab` when you need a PDF from scratch.
- **Edit / merge / screenshot pages**: use `pymupdf` (`fitz`).
- **Extract tables/text**: use `pdfplumber`.

See [media-processing.md](media-processing.md) for conversion utilities and [data-pipelines.md](data-pipelines.md) for end-to-end flows.
