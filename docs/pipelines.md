# Pipelines — Data Conversion Flows

> End-to-end workflows: source → transform → output → upload/email.

**Related:** [doc-forge.md](doc-forge.md) | [datastore.md](datastore.md) | [workspace.md](workspace.md) | [mailbox.md](mailbox.md)

---

## CSV → Styled Excel → Google Sheets

```python
import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

rows = list(csv.reader(open('data.csv')))
wb = Workbook()
ws = wb.active
for i, row in enumerate(rows):
    ws.append(row)
    if i == 0:
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", fill_type="solid")
wb.save('/tmp/data.xlsx')
```

```bash
# Upload as Google Sheet
gws drive files create --upload /tmp/data.xlsx \
  --upload-content-type application/vnd.openxmlformats-officedocument.spreadsheetml.sheet \
  --json '{"name":"Data Report","mimeType":"application/vnd.google-apps.spreadsheet"}'

# Share publicly
gws drive permissions create --params '{"fileId":"ID"}' --json '{"role":"reader","type":"anyone"}'
```

## PDF → Extract Data → Excel

```python
import pdfplumber
from openpyxl import Workbook

with pdfplumber.open('invoice.pdf') as pdf:
    tables = pdf.pages[0].extract_tables()

wb = Workbook()
ws = wb.active
for table in tables:
    for row in table: ws.append(row)
wb.save('/tmp/invoice_data.xlsx')
```

## Google Sheet ↔ Local Edit

```bash
# Download
gws drive files export --params '{"fileId":"ID",
  "mimeType":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}' \
  --output /tmp/sheet.xlsx
```

```python
from openpyxl import load_workbook
wb = load_workbook('/tmp/sheet.xlsx')
wb.active['A1'] = 'Updated'
wb.save('/tmp/sheet_updated.xlsx')
```

```bash
# Upload back
gws drive files update --params '{"fileId":"ID"}' --upload /tmp/sheet_updated.xlsx \
  --upload-content-type application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

## Database → Excel Report

```python
# 1. Query via mcp__mcp_server_mysql__mysql_query
# 2. Build styled Excel (see doc-forge.md)
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active
for i, name in enumerate(column_names, 1):
    c = ws.cell(row=1, column=i, value=name)
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = PatternFill(start_color="4472C4", fill_type="solid")
for ri, row in enumerate(results, 2):
    for ci, val in enumerate(row, 1):
        ws.cell(row=ri, column=ci, value=val)
wb.save('/tmp/query_export.xlsx')
```

## Database → Google Sheets (direct)

```python
values = [column_names] + [[str(v) for v in row] for row in results]
# Write as JSON to gws sheets values update
```

## JSON → Excel

```python
import json
from openpyxl import Workbook

data = json.load(open('data.json'))
wb = Workbook()
ws = wb.active
if isinstance(data, list) and data:
    headers = list(data[0].keys())
    ws.append(headers)
    for item in data:
        ws.append([item.get(h) for h in headers])
wb.save('/tmp/from_json.xlsx')
```

## HTML Table → Excel

```python
from bs4 import BeautifulSoup
from openpyxl import Workbook

soup = BeautifulSoup(open('page.html').read(), 'lxml')
wb = Workbook()
ws = wb.active
for row in soup.find('table').find_all('tr'):
    ws.append([td.get_text(strip=True) for td in row.find_all(['td', 'th'])])
wb.save('/tmp/from_html.xlsx')
```

## Excel → PDF

```python
from openpyxl import load_workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

rows = list(load_workbook('data.xlsx').active.iter_rows(values_only=True))
doc = SimpleDocTemplate("/tmp/output.pdf", pagesize=A4)
t = Table(rows)
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4472C4')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
]))
doc.build([t])
```

## Markdown → PDF Report

```bash
pandoc notes.md -o /tmp/report.pdf --toc \
  --metadata title="Report" --metadata date="2026-03-25"
gws drive files create --upload /tmp/report.pdf \
  --upload-content-type application/pdf --json '{"name":"Report.pdf"}'
```

## Full Pipeline: Collect → Analyze → Report → Email

```
1. Query database → mcp__mcp_server_mysql__mysql_query     (datastore.md)
2. Process data → Python aggregation/filtering
3. Create Excel with charts → openpyxl                      (doc-forge.md)
4. Generate PDF summary → reportlab                         (doc-forge.md)
5. Upload both to Drive → gws drive files create            (workspace.md)
6. Compose email with attachments → MIME                     (mailbox.md)
7. Send → gws gmail users messages send                      (workspace.md)
```
