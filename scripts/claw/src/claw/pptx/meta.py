"""claw pptx meta — get/set core deck properties."""

from __future__ import annotations

from pathlib import Path

import click

from claw.common import EXIT_INPUT, common_output_options, die, emit_json, safe_write


@click.group(name="meta")
def meta() -> None:
    """Get or set core deck properties."""


@meta.command(name="get")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--json", "as_json", is_flag=True)
@click.option("--layouts", is_flag=True,
              help="Enumerate master's layouts with placeholder info.")
def meta_get(src: Path, as_json: bool, layouts: bool) -> None:
    """Print core properties (and optionally layouts)."""
    try:
        from pptx import Presentation
    except ImportError:
        die("python-pptx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[pptx]'", as_json=as_json)

    prs = Presentation(str(src))
    p = prs.core_properties
    info = {
        "title": p.title, "author": p.author, "subject": p.subject,
        "keywords": p.keywords, "category": p.category, "comments": p.comments,
        "last_modified_by": p.last_modified_by,
        "created": p.created, "modified": p.modified,
        "slide_count": len(prs.slides),
    }

    if layouts:
        info["layouts"] = [
            {"index": i, "name": layout.name,
             "placeholder_types": [ph.placeholder_format.type
                                   and str(ph.placeholder_format.type)
                                   for ph in layout.placeholders]}
            for i, layout in enumerate(prs.slide_layouts)
        ]

    if as_json:
        emit_json(info)
    else:
        for k, v in info.items():
            if k == "layouts":
                click.echo("layouts:")
                for layout in v:
                    click.echo(f"  {layout['index']}: {layout['name']}")
            else:
                click.echo(f"{k}: {v}")


@meta.command(name="set")
@click.argument("src", type=click.Path(exists=True, path_type=Path))
@click.option("--title", default=None)
@click.option("--author", default=None)
@click.option("--subject", default=None)
@click.option("--keywords", default=None)
@click.option("--category", default=None)
@click.option("--comments", default=None)
@common_output_options
def meta_set(src: Path, title: str | None, author: str | None, subject: str | None,
             keywords: str | None, category: str | None, comments: str | None,
             force: bool, backup: bool, as_json: bool, dry_run: bool,
             quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Set core deck properties."""
    try:
        from pptx import Presentation
    except ImportError:
        die("python-pptx not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[pptx]'", as_json=as_json)

    updates = {"title": title, "author": author, "subject": subject,
               "keywords": keywords, "category": category, "comments": comments}

    if dry_run:
        click.echo(f"would set: {updates}")
        return

    prs = Presentation(str(src))
    for k, v in updates.items():
        if v is not None:
            setattr(prs.core_properties, k, v)

    def _save(f):
        prs.save(f)

    safe_write(src, _save, force=True, backup=backup, mkdir=mkdir)

    if as_json:
        emit_json({"path": str(src),
                   "updates": {k: v for k, v in updates.items() if v is not None}})
    elif not quiet:
        click.echo(f"updated metadata on {src}")
