"""claw pdf from-md — Markdown → PDF via reportlab PLATYPUS."""
from __future__ import annotations

import re
from pathlib import Path

import click

from claw.common import common_output_options, die, emit_json, safe_write


PAGE_SIZES = ("Letter", "A4", "Legal")
THEMES = ("minimal", "corporate", "academic", "dark")


def _parse_margin(spec: str) -> float:
    s = spec.strip().lower()
    if s.endswith("in"):
        return float(s[:-2]) * 72
    if s.endswith("cm"):
        return float(s[:-2]) * 28.3465
    if s.endswith("mm"):
        return float(s[:-2]) * 2.83465
    if s.endswith("pt"):
        return float(s[:-2])
    return float(s)


@click.command(name="from-md")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("out", type=click.Path(path_type=Path))
@click.option("--theme", type=click.Choice(THEMES), default="minimal")
@click.option("--page-size", type=click.Choice(PAGE_SIZES), default="Letter")
@click.option("--margin", default="1in")
@click.option("--toc", is_flag=True)
@click.option("--title", default=None)
@click.option("--author", default=None)
@common_output_options
def from_md(src: Path, out: Path, theme: str, page_size: str, margin: str,
            toc: bool, title: str | None, author: str | None,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Convert Markdown <SRC> to PDF <OUT>."""
    try:
        from reportlab.lib import pagesizes, colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, PageBreak,
            Preformatted, ListFlowable, ListItem,
        )
    except ImportError:
        die("reportlab not installed; install: pip install 'claw[pdf]'")

    text = src.read_text(encoding="utf-8")
    mgn = _parse_margin(margin)
    size = getattr(pagesizes, page_size)

    styles = getSampleStyleSheet()
    if theme == "dark":
        for name in ("BodyText", "Heading1", "Heading2", "Heading3"):
            styles[name].textColor = colors.whitesmoke
    if theme == "academic":
        styles["BodyText"].fontName = "Times-Roman"
    code_style = ParagraphStyle("code", parent=styles["Code"], fontSize=9,
                                leftIndent=12, backColor=colors.whitesmoke)

    story: list = []
    if title:
        story.append(Paragraph(title, styles["Title"]))
        if author:
            story.append(Paragraph(author, styles["Italic"]))
        story.append(Spacer(1, 18))

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            buf: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            story.append(Preformatted("\n".join(buf), code_style))
            story.append(Spacer(1, 8))
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            heading_style = styles.get(f"Heading{min(level, 4)}", styles["Heading1"])
            story.append(Paragraph(m.group(2), heading_style))
            i += 1
            continue
        if line.strip().startswith(("- ", "* ", "+ ")):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ", "+ ")):
                items.append(ListItem(Paragraph(lines[i].strip()[2:], styles["BodyText"])))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet"))
            story.append(Spacer(1, 6))
            continue
        if line.strip() == "":
            story.append(Spacer(1, 6))
            i += 1
            continue
        para: list[str] = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(
                r"^(#{1,6}\s|```|[\-\*\+]\s)", lines[i].strip()):
            para.append(lines[i])
            i += 1
        text_html = " ".join(para)
        text_html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text_html)
        text_html = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text_html)
        text_html = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text_html)
        story.append(Paragraph(text_html, styles["BodyText"]))

    if dry_run:
        click.echo(f"would render {src} → {out} ({theme}, {page_size})")
        return

    def build(f):
        doc = SimpleDocTemplate(f, pagesize=size,
                                leftMargin=mgn, rightMargin=mgn,
                                topMargin=mgn, bottomMargin=mgn,
                                title=title or src.stem, author=author or "")
        doc.build(story)

    safe_write(out, build, force=force, backup=backup, mkdir=mkdir)
    if as_json:
        emit_json({"out": str(out), "theme": theme, "page_size": page_size})
    elif not quiet:
        click.echo(f"wrote {out}")
