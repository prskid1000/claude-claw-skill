"""claw web links — enumerate anchor hrefs."""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import click

from claw.common import (
    EXIT_INPUT, common_output_options, die, emit_json, read_text, safe_write,
)


def _fetch_html(src: str) -> tuple[str, str]:
    """Return (html, base_url)."""
    if src == "-":
        return sys.stdin.read(), ""
    if src.startswith(("http://", "https://")):
        try:
            import httpx
        except ImportError:
            die("httpx not installed", code=EXIT_INPUT, hint="pip install 'claw[web]'")
        r = httpx.get(src, follow_redirects=True, timeout=30.0,
                      headers={"User-Agent": "claw/1.0"})
        r.raise_for_status()
        return r.text, str(r.url)
    return read_text(src), ""


def _matches_filter(expr: str, record: dict) -> bool:
    expr = expr.strip()
    if " contains " in expr:
        field, val = expr.split(" contains ", 1)
        return val.strip().strip("'\"") in (record.get(field.strip()) or "")
    if " == " in expr:
        field, val = expr.split(" == ", 1)
        return (record.get(field.strip()) or "") == val.strip().strip("'\"")
    if " startswith " in expr:
        field, val = expr.split(" startswith ", 1)
        return (record.get(field.strip()) or "").startswith(val.strip().strip("'\""))
    return True


@click.command(name="links")
@click.argument("src")
@click.option("--absolute", is_flag=True, help="Resolve relative URLs against --base.")
@click.option("--base", default=None, help="Base URL (default: fetched URL).")
@click.option("--filter", "filter_expr", default=None,
              help='E.g. "href contains \'docs\'".')
@click.option("--same-origin", is_flag=True, help="Only links from the same host.")
@click.option("--unique", is_flag=True, help="De-dupe by absolute URL.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]))
@click.option("--out", default=None, type=click.Path(path_type=Path))
@common_output_options
def links(src: str, absolute: bool, base: str | None, filter_expr: str | None,
          same_origin: bool, unique: bool, fmt: str, out: Path | None,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Enumerate <a href=...> from a URL / file / stdin."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        die("beautifulsoup4 not installed", code=EXIT_INPUT,
            hint="pip install 'claw[html]'", as_json=as_json)

    html, fetched_url = _fetch_html(src)
    soup = BeautifulSoup(html, "lxml")
    base_url = base or fetched_url or ""

    if dry_run:
        click.echo(f"would enumerate links from {src}")
        return

    origin_host = urlparse(base_url).netloc if same_origin and base_url else None
    seen: set[str] = set()
    out_records: list[dict] = []

    for a in soup.find_all("a"):
        href = a.get("href", "")
        if not href:
            continue
        abs_href = urljoin(base_url, href) if base_url else href
        rec = {
            "href": href,
            "text": a.get_text(strip=True),
            "rel": " ".join(a.get("rel", [])) if a.get("rel") else None,
            "title": a.get("title"),
            "absolute_href": abs_href,
        }
        if filter_expr and not _matches_filter(filter_expr, rec):
            continue
        if same_origin and origin_host and urlparse(abs_href).netloc not in ("", origin_host):
            continue
        key = abs_href if unique else None
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        out_records.append(rec)

    if fmt == "json" or as_json:
        lines = []
        for r in out_records:
            import json
            lines.append(json.dumps(r, ensure_ascii=False))
        content = "\n".join(lines) + ("\n" if lines else "")
    else:
        content = "\n".join((r["absolute_href"] if absolute else r["href"])
                            for r in out_records) + ("\n" if out_records else "")

    if out is None or str(out) == "-":
        sys.stdout.write(content)
    else:
        safe_write(out, lambda f: f.write(content.encode("utf-8")),
                   force=force, backup=backup, mkdir=mkdir)
        if not quiet:
            click.echo(f"wrote {out} ({len(out_records)} links)", err=True)
