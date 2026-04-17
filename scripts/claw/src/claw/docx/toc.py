"""claw docx toc — insert a Table of Contents field."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="toc")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--at", "anchor", default=None)
@click.option("--before/--after", "before", default=True)
@click.option("--levels", default="1-3", help='Heading levels to include, e.g. "1-3".')
@click.option("--title", default="Contents")
@common_output_options
def toc(src: Path, anchor: str | None, before: bool, levels: str, title: str,
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Insert a TOC field (Word recomputes on open)."""
    try:
        from docx import Document
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
    except ImportError:
        die("python-docx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[docx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would insert TOC (levels={levels})")
        return

    doc = Document(str(src))

    if title:
        title_p = doc.add_paragraph(title)
        try:
            title_p.style = doc.styles["Heading 1"]
        except KeyError:
            pass

    toc_para = doc.add_paragraph()
    run = toc_para.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.text = f'TOC \\o "{levels}" \\h \\z \\u'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)

    if anchor:
        target = next((p for p in doc.paragraphs if anchor in p.text
                       and p is not toc_para), None)
        if target is None:
            die(f"anchor not found: {anchor!r}", code=EXIT_INPUT, as_json=as_json)
        els = [title_p._p] if title else []
        els.append(toc_para._p)
        for el in reversed(els):
            el.getparent().remove(el)
            if before:
                target._p.addprevious(el)
            else:
                target._p.addnext(el)

    def _save(f):
        doc.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src), "levels": levels, "title": title})
    elif not quiet:
        click.echo(f"inserted TOC (levels={levels})")
