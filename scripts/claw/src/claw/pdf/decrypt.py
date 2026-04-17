"""claw pdf decrypt — strip password protection."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import common_output_options, die, emit_json, safe_write


@click.command(name="decrypt")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--password", "-p", required=True, help="Owner or user password.")
@click.option("-o", "--out", type=click.Path(path_type=Path), default=None)
@click.option("--in-place", is_flag=True)
@common_output_options
def decrypt(src: Path, password: str, out: Path | None, in_place: bool,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Decrypt <SRC> using --password."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        die("pypdf not installed; install: pip install 'claw[pdf]'")

    if not (out or in_place):
        die("pass --out FILE or --in-place", code=2)
    target = src if in_place else out
    assert target is not None

    reader = PdfReader(str(src))
    if reader.is_encrypted:
        ok = reader.decrypt(password)
        if not ok:
            die("password rejected", code=4)

    writer = PdfWriter(clone_from=reader)

    if dry_run:
        click.echo(f"would decrypt {src} → {target}")
        return

    safe_write(target, lambda f: writer.write(f),
               force=force or in_place, backup=backup, mkdir=mkdir)
    if as_json:
        emit_json({"out": str(target), "pages": len(reader.pages)})
    elif not quiet:
        click.echo(f"decrypted → {target}")
