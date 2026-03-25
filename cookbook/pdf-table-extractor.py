#!/usr/bin/env python3
"""
Cortex Example: pdf-table-extractor
Description: Extract tables from PDF to CSV files
Tags: pdf,tables,pdfplumber,extraction
Captured: 2026-03-25
Source: pdf-table-extractor.py

Usage:
  python ~/.claude/skills/cortex/cookbook/pdf-table-extractor.py
"""

#!/usr/bin/env python3
"""
Extract all tables from a PDF and save each as a CSV file.
Uses pdfplumber for accurate table detection.

Usage:
    python pdf-table-extractor.py input.pdf [output_dir]
"""

import sys
import csv
from pathlib import Path
import pdfplumber


def extract_tables(pdf_path, output_dir=None):
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir) if output_dir else pdf_path.parent / f"{pdf_path.stem}_tables"
    output_dir.mkdir(parents=True, exist_ok=True)

    table_count = 0

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables, 1):
                if not table or all(all(c is None for c in row) for row in table):
                    continue

                table_count += 1
                out_file = output_dir / f"page{page_num}_table{t_idx}.csv"

                with open(out_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    for row in table:
                        cleaned = [cell.strip() if cell else "" for cell in row]
                        writer.writerow(cleaned)

                print(f"  Extracted: {out_file.name} ({len(table)} rows)")

    if table_count == 0:
        print("No tables found in PDF.")
    else:
        print(f"\nTotal: {table_count} tables → {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf-table-extractor.py input.pdf [output_dir]")
        sys.exit(1)
    extract_tables(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
