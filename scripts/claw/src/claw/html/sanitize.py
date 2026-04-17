"""claw html sanitize — allow-list HTML cleanup via lxml_html_clean."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


_WARN = ("warning: claw html sanitize is a convenience tool, NOT a security boundary. "
         "For untrusted HTML destined for a browser, use `bleach` directly.\n")

_CATEGORY_MAP = {
    "scripts":  ("scripts", True),
    "iframes":  ("frames", True),
    "style":    ("style", True),
    "comments": ("comments", True),
    "forms":    ("forms", True),
    "embeds":   ("embedded", True),
}


@click.command(name="sanitize")
@click.argument("src")
@click.option("--allow", default=None, help="Comma-separated extra tags to keep.")
@click.option("--allow-attr", default=None,
              help="Comma-separated attrs to keep (default href,src,alt,title,class,id).")
@click.option("--remove", default="scripts,iframes,style,forms,embeds",
              help="Categories to remove.")
@click.option("--strip-unknown", is_flag=True,
              help="Decompose unknown tags instead of unwrapping.")
@click.option("--in-place", is_flag=True)
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def sanitize(src: str, allow: str | None, allow_attr: str | None, remove: str,
             strip_unknown: bool, in_place: bool, out: Path | None,
             force: bool, backup: bool, as_json: bool, dry_run: bool,
             quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Allow-list sanitization (not a security boundary — use bleach for that)."""
    try:
        from lxml_html_clean import Cleaner
    except ImportError:
        try:
            from lxml.html.clean import Cleaner
        except ImportError:
            die("lxml_html_clean not installed", code=EXIT_INPUT,
                hint="pip install 'claw[html]'", as_json=as_json)

    sys.stderr.write(_WARN)
    html = read_text(src)

    if dry_run:
        click.echo(f"would sanitize {src}")
        return

    kwargs: dict = {
        "scripts": False, "javascript": True, "comments": False,
        "style": False, "inline_style": True, "links": False,
        "meta": False, "page_structure": False, "processing_instructions": True,
        "embedded": False, "frames": False, "forms": False,
        "annoying_tags": False, "safe_attrs_only": True,
    }
    default_attrs = {"href", "src", "alt", "title", "class", "id"}
    if allow_attr:
        default_attrs |= {a.strip() for a in allow_attr.split(",") if a.strip()}
    kwargs["safe_attrs"] = frozenset(default_attrs)

    for cat in (c.strip() for c in remove.split(",")):
        if cat in _CATEGORY_MAP:
            flag, val = _CATEGORY_MAP[cat]
            kwargs[flag] = val

    if allow:
        extra = [t.strip() for t in allow.split(",") if t.strip()]
        kwargs["remove_unknown_tags"] = False
        kwargs["allow_tags"] = None
        if not strip_unknown:
            kwargs["remove_unknown_tags"] = False

    cleaner = Cleaner(**{k: v for k, v in kwargs.items() if k != "allow_tags"})
    from lxml import html as lxml_html, etree
    tree = lxml_html.fromstring(html)
    cleaned = cleaner.clean_html(tree)
    result = etree.tostring(cleaned, encoding="unicode", method="html")

    dst = Path(src) if in_place and src != "-" else out
    if dst is None or str(dst) == "-":
        sys.stdout.write(result)
    else:
        safe_write(dst, lambda f: f.write(result.encode("utf-8")),
                   force=force or in_place, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {dst}", err=True)

    if as_json:
        emit_json({"output_bytes": len(result.encode("utf-8"))})
