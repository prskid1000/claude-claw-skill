#!/usr/bin/env python3
"""
Cortex Example: invoice-pdf-generator
Description: Generate professional PDF invoices from JSON data
Tags: pdf,invoice,reportlab,finance
Captured: 2026-03-25
Source: invoice-pdf-generator.py

Usage:
  python ~/.claude/skills/cortex/cookbook/invoice-pdf-generator.py
"""

#!/usr/bin/env python3
"""
Generate a professional PDF invoice from a JSON data file.
Uses reportlab for layout.

Usage:
    python invoice-pdf-generator.py invoice_data.json [output.pdf]

JSON format:
{
    "invoice_number": "INV-001",
    "date": "<YYYY-MM-DD>",
    "due_date": "<YYYY-MM-DD>",
    "company": {"name": "Acme Corp", "address": "123 Main St", "email": "user@acme.com"},
    "client": {"name": "Client Inc", "address": "456 Oak Ave", "email": "user@client.com"},
    "items": [
        {"description": "Web Development", "qty": 40, "unit_price": 150.00},
        {"description": "Design Services", "qty": 10, "unit_price": 120.00}
    ],
    "tax_rate": 0.05,
    "notes": "Payment due within 30 days."
}
"""

import sys
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_invoice(data, output_path):
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("InvTitle", parent=styles["Heading1"], fontSize=24, textColor=colors.HexColor("#2B579A"))
    elements = []

    # Header
    elements.append(Paragraph(data["company"]["name"], title_style))
    elements.append(Paragraph(data["company"]["address"], styles["Normal"]))
    elements.append(Paragraph(data["company"]["email"], styles["Normal"]))
    elements.append(Spacer(1, 10*mm))

    # Invoice details
    details = [
        ["INVOICE", f"#{data['invoice_number']}"],
        ["Date", data["date"]],
        ["Due Date", data["due_date"]],
        ["Bill To", data["client"]["name"]],
        ["", data["client"]["address"]],
    ]
    t = Table(details, colWidths=[40*mm, 120*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (1, 0), 14),
        ("TEXTCOLOR", (0, 0), (1, 0), colors.HexColor("#2B579A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10*mm))

    # Items table
    header = ["Description", "Qty", "Unit Price", "Total"]
    rows = [header]
    subtotal = 0
    for item in data["items"]:
        total = item["qty"] * item["unit_price"]
        subtotal += total
        rows.append([
            item["description"],
            str(item["qty"]),
            f"${item['unit_price']:,.2f}",
            f"${total:,.2f}",
        ])

    tax = subtotal * data.get("tax_rate", 0)
    grand_total = subtotal + tax

    rows.append(["", "", "Subtotal", f"${subtotal:,.2f}"])
    rows.append(["", "", f"Tax ({data.get('tax_rate', 0)*100:.0f}%)", f"${tax:,.2f}"])
    rows.append(["", "", "TOTAL", f"${grand_total:,.2f}"])

    t = Table(rows, colWidths=[80*mm, 20*mm, 35*mm, 35*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B579A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, len(data["items"])), 0.5, colors.grey),
        ("FONTNAME", (2, -1), (3, -1), "Helvetica-Bold"),
        ("FONTSIZE", (2, -1), (3, -1), 12),
        ("LINEABOVE", (2, -3), (3, -3), 1, colors.grey),
        ("LINEABOVE", (2, -1), (3, -1), 2, colors.HexColor("#2B579A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)

    # Notes
    if data.get("notes"):
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph("<b>Notes:</b>", styles["Normal"]))
        elements.append(Paragraph(data["notes"], styles["Normal"]))

    doc.build(elements)
    print(f"Invoice saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python invoice-pdf-generator.py invoice_data.json [output.pdf]")
        sys.exit(1)

    data_path = Path(sys.argv[1])
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    output = sys.argv[2] if len(sys.argv) > 2 else str(data_path.with_suffix(".pdf"))
    generate_invoice(data, output)
