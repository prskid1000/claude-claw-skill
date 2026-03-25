#!/usr/bin/env python3
"""
Cortex Example: excel-to-google-sheets
Description: Upload Excel to Google Sheets with shareable link
Tags: excel,sheets,gws,upload
Captured: 2026-03-25
Source: excel-to-google-sheets.py

Usage:
  python ~/.claude/skills/cortex/cookbook/excel-to-google-sheets.py
"""

#!/usr/bin/env python3
"""
Upload an Excel file to Google Sheets and return a shareable link.
Uses gws CLI for Google Workspace integration.

Usage:
    python excel-to-google-sheets.py input.xlsx [sheet_name] [folder_id]
"""

import sys
import json
import subprocess
from pathlib import Path


def run_gws(args, timeout=30):
    result = subprocess.run(
        f"gws {args}", shell=True, capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        raise RuntimeError(f"gws error: {result.stderr.strip()}")
    return result.stdout.strip()


def upload_to_sheets(xlsx_path, sheet_name=None, folder_id=None):
    xlsx_path = Path(xlsx_path)
    if not xlsx_path.exists():
        print(f"Error: File not found: {xlsx_path}")
        sys.exit(1)

    name = sheet_name or xlsx_path.stem

    # Upload file to Drive
    upload_args = f'drive files upload "{xlsx_path}" --format json'
    if folder_id:
        upload_args += f" --parent {folder_id}"
    result = json.loads(run_gws(upload_args))
    file_id = result.get("id")
    print(f"Uploaded: {file_id}")

    # Convert to Google Sheets format
    copy_args = f'drive files copy {file_id} --name "{name}" --mime-type application/vnd.google-apps.spreadsheet --format json'
    copy_result = json.loads(run_gws(copy_args))
    sheet_id = copy_result.get("id")

    # Delete original uploaded file
    run_gws(f"drive files delete {file_id} --confirm")

    # Set sharing to anyone with link
    run_gws(f'drive permissions create {sheet_id} --role reader --type anyone')

    link = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
    print(f"\nGoogle Sheets link: {link}")
    return link


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python excel-to-google-sheets.py input.xlsx [sheet_name] [folder_id]")
        sys.exit(1)
    upload_to_sheets(
        sys.argv[1],
        sys.argv[2] if len(sys.argv) > 2 else None,
        sys.argv[3] if len(sys.argv) > 3 else None,
    )
