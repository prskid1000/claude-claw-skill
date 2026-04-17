"""claw pdf encrypt — password-protect a PDF with access flags."""
from __future__ import annotations

from pathlib import Path

import click

from claw.common import common_output_options, die, emit_json, safe_write


PERMS = ("print", "copy", "modify", "annotate", "fill-forms", "assemble", "print-high")


def _build_permissions(allow: str | None, deny: str | None):
    from pypdf.constants import UserAccessPermissions as UAP

    mapping = {
        "print": UAP.PRINT,
        "copy": UAP.EXTRACT,
        "modify": UAP.MODIFY,
        "annotate": UAP.ADD_OR_MODIFY,
        "fill-forms": UAP.FILL_FORM_FIELDS,
        "assemble": UAP.ASSEMBLE_DOC,
        "print-high": UAP.PRINT_TO_REPRESENTATION,
    }
    if allow:
        names = [x.strip() for x in allow.split(",") if x.strip()]
        flags = UAP(0)
        for n in names:
            if n not in mapping:
                die(f"unknown permission: {n}; valid: {', '.join(mapping)}")
            flags |= mapping[n]
        return flags
    if deny:
        names = [x.strip() for x in deny.split(",") if x.strip()]
        flags = UAP.R2 | UAP.R3
        for n in names:
            if n not in mapping:
                die(f"unknown permission: {n}; valid: {', '.join(mapping)}")
            flags &= ~mapping[n]
        return flags
    return UAP(0)


@click.command(name="encrypt")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--password", "-p", required=True, help="User password.")
@click.option("--owner-password", default=None, help="Owner password (default = user).")
@click.option("--aes256", "algo", flag_value="AES-256", help="AES-256 (needs pycryptodome).")
@click.option("--aes128", "algo", flag_value="AES-128", default=True)
@click.option("--rc4-128", "algo", flag_value="RC4-128")
@click.option("--allow", default=None, help=f"CSV subset: {','.join(PERMS)}")
@click.option("--deny", default=None, help="CSV subset to deny.")
@click.option("-o", "--out", type=click.Path(path_type=Path), required=True)
@common_output_options
def encrypt(src: Path, password: str, owner_password: str | None, algo: str,
            allow: str | None, deny: str | None, out: Path,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Encrypt <SRC> with --password."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        die("pypdf not installed; install: pip install 'claw[pdf]'")

    if allow and deny:
        die("--allow and --deny are mutually exclusive", code=2)

    reader = PdfReader(str(src))
    writer = PdfWriter(clone_from=reader)
    perms = _build_permissions(allow, deny)

    kwargs = {"user_password": password,
              "owner_password": owner_password or password,
              "algorithm": algo,
              "permissions_flag": perms}

    try:
        writer.encrypt(**kwargs)
    except (ImportError, ModuleNotFoundError):
        die(f"{algo} requires pycryptodome; install: pip install 'claw[crypto]'")

    if dry_run:
        click.echo(f"would encrypt {src} with {algo} → {out}")
        return

    safe_write(out, lambda f: writer.write(f), force=force, backup=backup, mkdir=mkdir)
    if as_json:
        emit_json({"out": str(out), "algorithm": algo,
                   "allow": allow, "deny": deny})
    elif not quiet:
        click.echo(f"encrypted → {out} ({algo})")
