# Datastore — MySQL Database

> Query, explore, and export data via the MySQL MCP tool.

**Related:** [pipelines.md](pipelines.md) | [doc-forge.md](doc-forge.md) | [workspace.md](workspace.md)

---

## MCP Tool

```
mcp__mcp_server_mysql__mysql_query(query="SQL HERE")
```

**Safety:** Always LIMIT exploratory queries. Prefer SELECT. Test WHERE with SELECT before UPDATE/DELETE.

## Schema Exploration

```sql
SHOW DATABASES;
USE database_name;
SHOW TABLES;
DESCRIBE table_name;
SHOW CREATE TABLE table_name;

-- Column details
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'db' AND TABLE_NAME = 'tbl'
ORDER BY ORDINAL_POSITION;

-- Foreign keys
SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'db' AND REFERENCED_TABLE_NAME IS NOT NULL;

-- Indexes
SHOW INDEX FROM table_name;

-- Table sizes
SELECT TABLE_NAME, TABLE_ROWS,
  ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS size_mb
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'db' ORDER BY size_mb DESC;
```

## Common Queries

```sql
-- Basics
SELECT * FROM tbl LIMIT 20;
SELECT DISTINCT col FROM tbl;
SELECT col, COUNT(*) AS cnt FROM tbl GROUP BY col ORDER BY cnt DESC;

-- Date ranges
SELECT * FROM tbl WHERE created_at BETWEEN '2026-03-01' AND '2026-03-25';
SELECT * FROM tbl ORDER BY id DESC LIMIT 20;

-- NULL analysis
SELECT COUNT(*) total, COUNT(col) non_null, COUNT(*)-COUNT(col) nulls FROM tbl;

-- Aggregates
SELECT MIN(col), MAX(col), AVG(col), SUM(col) FROM tbl;

-- Search
SELECT * FROM tbl WHERE name LIKE '%term%';
SELECT * FROM tbl WHERE col REGEXP '^[A-Z]{2}[0-9]+';
```

## Joins

```sql
-- Inner
SELECT a.*, b.name FROM orders a JOIN customers b ON a.customer_id = b.id;

-- Find orphans
SELECT a.* FROM orders a LEFT JOIN customers b ON a.customer_id = b.id WHERE b.id IS NULL;

-- Multi-table
SELECT o.id, c.name, p.product_name, oi.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;
```

## Analytics

```sql
-- Pivot
SELECT date,
  SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) active,
  SUM(CASE WHEN status='inactive' THEN 1 ELSE 0 END) inactive
FROM tbl GROUP BY date;

-- Running total
SELECT date, amount, SUM(amount) OVER (ORDER BY date) running FROM transactions;

-- Rank
SELECT name, score, RANK() OVER (ORDER BY score DESC) rank FROM leaderboard;

-- Duplicates
SELECT col, COUNT(*) cnt FROM tbl GROUP BY col HAVING cnt > 1;

-- Date formatting
SELECT DATE_FORMAT(created_at, '%Y-%m-%d') date, DATE_FORMAT(created_at, '%H:%i') time FROM tbl;
```

## Performance

```sql
EXPLAIN SELECT * FROM tbl WHERE col = 'val';
EXPLAIN ANALYZE SELECT ...;
SHOW PROCESSLIST;
SHOW TABLE STATUS LIKE 'tbl';
```

## Export Patterns

### → Excel

```python
from openpyxl import Workbook
wb = Workbook()
ws = wb.active
ws.append(column_names)
for row in results: ws.append(row)
wb.save('/tmp/export.xlsx')
```

### → CSV

```python
import csv
with open('/tmp/export.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(column_names)
    w.writerows(results)
```

### → Google Sheets

```python
values = [column_names] + [[str(v) for v in row] for row in results]
# → gws sheets values update with values JSON
```

See [pipelines.md](pipelines.md) for full end-to-end export workflows.
