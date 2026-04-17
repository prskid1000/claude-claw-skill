"""claw docx new — create a blank .docx."""

from __future__ import annotations

import shutil
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="new")
@click.argument("out", type=click.Path(path_type=Path))
@click.option("--template", "template", default=None,
              type=click.Path(exists=True, path_type=Path),
              help="Existing .docx whose body is cleared but styles preserved.")
@common_output_options
def new(out: Path, template: Path | None,
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Create a blank .docx, optionally cloning a template's styles."""
    try:
        from docx import Document
    except ImportError:
        die("python-docx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[docx]'", as_json=as_json)

    if dry_run:
        click.echo(f"would write {out}" + (f" (template={template})" if template else ""))
        return

    if template:
        import tempfile
        tmp = Path(tempfile.mkstemp(suffix=".docx")[1])
        shutil.copy2(template, tmp)
        doc = Document(str(tmp))
        body = doc.element.body
        for p in list(body):
            if p.tag.endswith("}p") or p.tag.endswith("}tbl"):
                body.remove(p)
        tmp.unlink(missing_ok=True)
    else:
        doc = Document()

    def _save(f):
        doc.save(f)

    safe_write(out, _save, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(out), "template": str(template) if template else None})
    elif not quiet:
        click.echo(f"wrote {out}")
