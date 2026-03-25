#!/usr/bin/env python3
"""
Cortex Example: html-to-pdf
Description: Convert HTML to styled PDF using pymupdf
Tags: html,pdf,pymupdf,conversion
Captured: 2026-03-25
Source: html-to-pdf.py

Usage:
  python ~/.claude/skills/cortex/cookbook/html-to-pdf.py
"""

#!/usr/bin/env python3
"""
Convert HTML string or file to a styled PDF using pymupdf (fitz).
Supports inline CSS, images, and tables.

Usage:
    python html-to-pdf.py input.html [output.pdf]
    echo "<h1>Hello</h1><p>World</p>" | python html-to-pdf.py - output.pdf
"""

import sys
from pathlib import Path
import fitz  # pymupdf


def html_to_pdf(html_content, output_path):
    # Create a Story from HTML
    story = fitz.Story(html_content)

    # A4 page dimensions
    page_width = 595.28  # A4 width in points
    page_height = 841.89  # A4 height in points
    margin = 50

    content_rect = fitz.Rect(margin, margin, page_width - margin, page_height - margin)

    writer = fitz.DocumentWriter(str(output_path))

    more = True
    while more:
        dev = writer.begin_page(fitz.Rect(0, 0, page_width, page_height))
        more, _ = story.place(content_rect)
        story.draw(dev)
        writer.end_page()

    writer.close()
    print(f"PDF saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html-to-pdf.py input.html [output.pdf]")
        sys.exit(1)

    input_arg = sys.argv[1]

    if input_arg == "-":
        html = sys.stdin.read()
        output = sys.argv[2] if len(sys.argv) > 2 else "output.pdf"
    else:
        input_path = Path(input_arg)
        html = input_path.read_text(encoding="utf-8")
        output = sys.argv[2] if len(sys.argv) > 2 else str(input_path.with_suffix(".pdf"))

    html_to_pdf(html, output)
