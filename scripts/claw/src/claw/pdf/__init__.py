"""claw pdf — PDF operations. See references/claw/pdf.md."""

import click

from claw.common import LazyGroup

VERBS: dict[str, tuple[str, str]] = {
    "extract-text":   ("claw.pdf.extract_text", "extract_text"),
    "extract-tables": ("claw.pdf.extract_tables", "extract_tables"),
    "extract-images": ("claw.pdf.extract_images", "extract_images"),
    "render":         ("claw.pdf.render", "render"),
    "merge":          ("claw.pdf.merge", "merge"),
    "split":          ("claw.pdf.split", "split_"),
    "rotate":         ("claw.pdf.rotate", "rotate"),
    "watermark":      ("claw.pdf.watermark", "watermark"),
    "redact":         ("claw.pdf.redact", "redact"),
    "encrypt":        ("claw.pdf.encrypt", "encrypt"),
    "decrypt":        ("claw.pdf.decrypt", "decrypt"),
    "flatten":        ("claw.pdf.flatten", "flatten"),
    "ocr":            ("claw.pdf.ocr", "ocr"),
    "info":           ("claw.pdf.info", "info"),
    "from-html":      ("claw.pdf.from_html", "from_html"),
    "from-md":        ("claw.pdf.from_md", "from_md"),
    "qr":             ("claw.pdf.qr", "qr"),
    "search":         ("claw.pdf.search", "search"),
}


@click.command(cls=LazyGroup, lazy_commands=VERBS,
               context_settings={"help_option_names": ["-h", "--help"]})
def group() -> None:
    """PDF — extract, render, merge/split, redact/encrypt, OCR, from-html/md, QR."""
