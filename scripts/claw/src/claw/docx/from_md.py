"""claw docx from-md — convert Markdown to .docx via pandoc."""

from __future__ import annotations

import subprocess
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write, which,
)


@click.command(name="from-md")
@click.argument("out", type=click.Path(path_type=Path))
@click.option("--data", "data_src", required=True, help="Markdown file or - for stdin.")
@click.option("--reference", "reference_doc", default=None,
              type=click.Path(exists=True, path_type=Path))
@click.option("--toc", is_flag=True)
@click.option("--number-sections", "number_sections", is_flag=True)
@common_output_options
def from_md(out: Path, data_src: str, reference_doc: Path | None,
            toc: bool, number_sections: bool,
            force: bool, backup: bool, as_json: bool, dry_run: bool,
            quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Convert Markdown (file or stdin) to .docx using pandoc."""
    if not which("pandoc"):
        die("pandoc not found on PATH", code=EXIT_INPUT,
            hint="winget install JohnMacFarlane.Pandoc", as_json=as_json)

    md_text = read_text(data_src)

    if dry_run:
        click.echo(f"would write {out} via pandoc ({len(md_text)} chars)")
        return

    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                     encoding="utf-8") as tf:
        tf.write(md_text)
        md_tmp = Path(tf.name)
    tmp_out = out.with_suffix(out.suffix + ".tmp-pandoc")

    args = ["pandoc", str(md_tmp), "-f", "markdown", "-t", "docx", "-o", str(tmp_out)]
    if reference_doc:
        args += ["--reference-doc", str(reference_doc)]
    if toc:
        args += ["--toc"]
    if number_sections:
        args += ["--number-sections"]

    try:
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode != 0:
            die(f"pandoc failed: {result.stderr}", code=EXIT_INPUT, as_json=as_json)

        def _writer(f):
            f.write(tmp_out.read_bytes())

        safe_write(out, _writer, force=force, backup=backup, mkdir=mkdir)
    finally:
        md_tmp.unlink(missing_ok=True)
        tmp_out.unlink(missing_ok=True)

    if as_json:
        emit_json({"path": str(out), "source_chars": len(md_text)})
    elif not quiet:
        click.echo(f"wrote {out}")
