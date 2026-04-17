"""claw pdf flatten — bake forms and annotations into static content."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import common_output_options, die, emit_json, safe_write


@click.command(name="flatten")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--forms/--no-forms", default=True, help="Flatten AcroForm/XFA widgets.")
@click.option("--annotations/--no-annotations", default=False,
              help="Flatten highlight/note/ink annotations.")
@click.option("-o", "--out", type=click.Path(path_type=Path), default=None)
@click.option("--in-place", is_flag=True)
@common_output_options
def flatten(src: Path, forms: bool, annotations: bool, out: Path | None, in_place: bool,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Bake form fields and annotations of <SRC> into page content."""
    try:
        import fitz
    except ImportError:
        die("PyMuPDF not installed; install: pip install 'claw[pdf]'")

    if not (out or in_place):
        die("pass --out FILE or --in-place", code=2)
    target = src if in_place else out
    assert target is not None

    doc = fitz.open(str(src))
    try:
        if forms:
            if hasattr(doc, "bake"):
                doc.bake(annots=annotations, widgets=True)
            elif hasattr(doc, "bake_widgets"):
                doc.bake_widgets()
        elif annotations and hasattr(doc, "bake"):
            doc.bake(annots=True, widgets=False)

        if dry_run:
            click.echo(f"would flatten forms={forms} annots={annotations} → {target}")
            return

        data = doc.tobytes(deflate=True, garbage=4)
    finally:
        doc.close()

    safe_write(target, lambda f: f.write(data),
               force=force or in_place, backup=backup, mkdir=mkdir)
    if as_json:
        emit_json({"out": str(target), "forms": forms, "annotations": annotations})
    elif not quiet:
        click.echo(f"flattened → {target}")
