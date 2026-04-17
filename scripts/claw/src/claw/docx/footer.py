"""claw docx footer — set footer text on a section."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="footer")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--text", default="")
@click.option("--page-number", "page_number", is_flag=True, help="Append a PAGE field.")
@click.option("--section", default=None, type=int)
@click.option("--align", default=None,
              type=click.Choice(["left", "center", "right"]))
@common_output_options
def footer(src: Path, text: str, page_number: bool,
           section: int | None, align: str | None,
           force: bool, backup: bool, as_json: bool, dry_run: bool,
           quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Set the footer text (optionally with a PAGE field) on a section."""
    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
        from docx.oxml import OxmlElement
    except ImportError:
        die("python-docx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[docx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would set footer: {text}" + (" + PAGE" if page_number else ""))
        return

    doc = Document(str(src))
    sections = [doc.sections[section - 1]] if section else list(doc.sections)

    for sec in sections:
        f = sec.footer
        p = f.paragraphs[0] if f.paragraphs else f.add_paragraph()
        p.text = text
        if align:
            p.alignment = getattr(WD_ALIGN_PARAGRAPH, align.upper())
        if page_number:
            run = p.add_run()
            fld_begin = OxmlElement("w:fldChar")
            fld_begin.set(qn("w:fldCharType"), "begin")
            instr = OxmlElement("w:instrText")
            instr.text = "PAGE"
            fld_end = OxmlElement("w:fldChar")
            fld_end.set(qn("w:fldCharType"), "end")
            run._r.append(fld_begin)
            run._r.append(instr)
            run._r.append(fld_end)

    def _save(f):
        doc.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "footer": text, "page_number": page_number})
    elif not quiet:
        click.echo(f"set footer on {len(sections)} section(s)")
