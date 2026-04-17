"""claw web extract — trafilatura main-article extraction."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write, write_text,
)


@click.command(name="extract")
@click.argument("src")
@click.option("--precision", "preset", flag_value="precision", help="Tighter filtering.")
@click.option("--recall", "preset", flag_value="recall", help="Permissive.")
@click.option("--balanced", "preset", flag_value="balanced", default=True,
              help="Middle ground (default).")
@click.option("--include-comments", is_flag=True)
@click.option("--include-tables", is_flag=True, default=True)
@click.option("--format", "fmt", default="text",
              type=click.Choice(["text", "md", "markdown", "json", "xml"]))
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def extract(src: str, preset: str, include_comments: bool, include_tables: bool,
            fmt: str, out: Path | None, force: bool, backup: bool, as_json: bool,
            dry_run: bool, quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Extract main article text from a URL or HTML on stdin (pass `-`)."""
    try:
        import trafilatura
    except ImportError:
        die("trafilatura not installed", code=EXIT_INPUT,
            hint="pip install 'claw[web]'", as_json=as_json)

    if src == "-":
        html = sys.stdin.read()
    elif src.startswith(("http://", "https://")):
        html = trafilatura.fetch_url(src)
        if not html:
            die(f"could not fetch {src}", code=EXIT_INPUT, as_json=as_json)
    else:
        html = read_text(src)

    if dry_run:
        click.echo(f"would extract from {src} (preset={preset}, format={fmt})")
        return

    output_format = {"md": "markdown", "markdown": "markdown",
                     "text": "txt", "json": "json", "xml": "xml"}[fmt]
    kwargs: dict = {
        "output_format": output_format,
        "include_comments": include_comments,
        "include_tables": include_tables,
    }
    if preset == "precision":
        kwargs["favor_precision"] = True
    elif preset == "recall":
        kwargs["favor_recall"] = True

    result = trafilatura.extract(html, **kwargs)
    if not result:
        die("extraction produced no content", code=EXIT_INPUT, as_json=as_json)

    if out is None or str(out) == "-":
        if as_json and fmt != "json":
            emit_json({"format": fmt, "content": result})
        else:
            sys.stdout.write(result)
            if not result.endswith("\n"):
                sys.stdout.write("\n")
    else:
        safe_write(out, lambda f: f.write(result.encode("utf-8")),
                   force=force, backup=backup, mkdir=mkdir)
        if as_json:
            emit_json({"out": str(out), "bytes": len(result.encode("utf-8"))})
        elif not quiet:
            click.echo(f"wrote {out}")
