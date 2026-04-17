"""claw pptx new — create a blank .pptx."""

from __future__ import annotations

import shutil
from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.command(name="new",
               context_settings={"ignore_unknown_options": True,
                                 "allow_extra_args": True})
@click.argument("out", type=click.Path(path_type=Path))
@click.option("--template", default=None,
              type=click.Path(exists=True, path_type=Path))
@common_output_options
@click.pass_context
def new(ctx: click.Context, out: Path, template: Path | None,
        force: bool, backup: bool, as_json: bool, dry_run: bool,
        quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Create a blank .pptx (optionally from a template)."""
    try:
        from pptx import Presentation
        from pptx.util import Emu
    except ImportError:
        die("python-pptx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[pptx]'", as_json=as_json)

    aspect = "16:9"
    for arg in ctx.args:
        if arg == "--4:3":
            aspect = "4:3"
        elif arg == "--16:9":
            aspect = "16:9"

    if dry_run:
        click.echo(f"would write {out} ({aspect})"
                   + (f" from {template}" if template else ""))
        return

    if template:
        import tempfile
        tmp = Path(tempfile.mkstemp(suffix=".pptx")[1])
        shutil.copy2(template, tmp)
        prs = Presentation(str(tmp))
        sldIdLst = prs.slides._sldIdLst
        for sldId in list(sldIdLst):
            rId = sldId.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            prs.part.drop_rel(rId)
            sldIdLst.remove(sldId)
        tmp.unlink(missing_ok=True)
    else:
        prs = Presentation()

    if not template:
        if aspect == "16:9":
            prs.slide_width = Emu(12192000)
            prs.slide_height = Emu(6858000)
        else:
            prs.slide_width = Emu(9144000)
            prs.slide_height = Emu(6858000)

    def _save(f):
        prs.save(f)

    safe_write(out, _save, force=force, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(out), "aspect": aspect,
                   "template": str(template) if template else None})
    elif not quiet:
        click.echo(f"wrote {out}")
