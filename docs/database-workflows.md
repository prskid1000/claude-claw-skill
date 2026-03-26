# Database Workflows — Query / Explore / Export (MySQL MCP)

> Query, explore, and export data via the MySQL MCP tool.

**Related:** [data-pipelines.md](data-pipelines.md) | [create-documents.md](create-documents.md) | [gws-quickref.md](gws-quickref.md)

---

## MCP Tool

```
mcp__mcp_server_mysql__mysql_query(query="SQL HERE")
```

## Safe usage (recommended)

- **Start read-only**: prefer `SELECT` until you’re certain.
- **Always cap**: include `LIMIT` in exploratory queries.
- **Small surface area**: select only the columns you need.
- **Filter carefully**: validate your `WHERE` with a `SELECT` before any update/delete work.
- **Avoid heavy scans**: add a restrictive `WHERE`, avoid unbounded joins on large tables.

## Quick schema checklist (minimal)

- **What DB/tables exist?**: `SHOW DATABASES`, `SHOW TABLES`
- **What columns/types?**: `DESCRIBE table_name` or `SHOW CREATE TABLE table_name`
- **What’s big?**: check row counts / sizes before running expensive queries

## Export patterns

You usually want: `column_names` + `rows` from the MCP call, then write one of:

### → Excel (quick)

```python
from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.append(column_names)
for row in rows:
    ws.append(list(row))
wb.save("/tmp/export.xlsx")
```

### → CSV (quick)

```python
import csv

with open("/tmp/export.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(column_names)
    w.writerows(rows)
```

### → Google Sheets (pattern)

Build `values = [column_names] + [[str(v) for v in row] for row in rows]` and write via `gws sheets ... values update`.

See [data-pipelines.md](data-pipelines.md) for full end-to-end export workflows.
