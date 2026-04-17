"""claw doc read — dump a Doc as text / json / markdown."""

from __future__ import annotations

import json
from pathlib import Path

import click

from claw.common import EXIT_SYSTEM, common_output_options, die, emit_json, gws_run, write_text


def _extract_runs(paragraph: dict) -> list[dict]:
    runs = []
    for el in paragraph.get("elements", []):
        tr = el.get("textRun")
        if not tr:
            continue
        runs.append({"text": tr.get("content", ""), "style": tr.get("textStyle", {})})
    return runs


def _style_to_md(text: str, style: dict) -> str:
    if style.get("weightedFontFamily", {}).get("fontFamily") == "Consolas":
        return f"`{text}`"
    if "link" in style and style["link"].get("url"):
        return f"[{text}]({style['link']['url']})"
    if style.get("bold") and style.get("italic"):
        return f"***{text}***"
    if style.get("bold"):
        return f"**{text}**"
    if style.get("italic"):
        return f"*{text}*"
    return text


def _walk_body(body: dict, fmt: str) -> str:
    out: list[str] = []
    for elt in body.get("content", []):
        para = elt.get("paragraph")
        if not para:
            continue
        runs = _extract_runs(para)
        text = "".join(r["text"] for r in runs).rstrip("\n")
        if fmt == "text":
            out.append(text)
            continue
        style = para.get("paragraphStyle", {}).get("namedStyleType", "NORMAL_TEXT")
        bullet = para.get("bullet") is not None
        if style == "TITLE":
            out.append(f"# {text}")
        elif style == "HEADING_1":
            out.append(f"## {text}")
        elif style == "HEADING_2":
            out.append(f"### {text}")
        elif style == "HEADING_3":
            out.append(f"#### {text}")
        elif style == "HEADING_4":
            out.append(f"##### {text}")
        elif style == "HEADING_5":
            out.append(f"###### {text}")
        elif bullet:
            styled = "".join(_style_to_md(r["text"], r["style"]) for r in runs).rstrip("\n")
            out.append(f"- {styled}")
        else:
            styled = "".join(_style_to_md(r["text"], r["style"]) for r in runs).rstrip("\n")
            out.append(styled)
    return "\n\n".join(s for s in out if s)


def _find_body(doc: dict, tab_id: str | None) -> dict:
    if tab_id:
        for tab in doc.get("tabs", []) or []:
            if tab.get("tabProperties", {}).get("tabId") == tab_id:
                return tab.get("documentTab", {}).get("body", {})
    tabs = doc.get("tabs", []) or []
    if tabs:
        return tabs[0].get("documentTab", {}).get("body", {})
    return doc.get("body", {})


@click.command(name="read")
@click.argument("doc_id")
@click.option("--tab", "tab_id", default=None)
@click.option("--format", "fmt", type=click.Choice(["text", "json", "md"]), default="text")
@click.option("--out", default="-", type=click.Path())
@common_output_options
def read(doc_id, tab_id, fmt, out,
         force, backup, as_json, dry_run, quiet, verbose, mkdir) -> None:
    """Read a Doc."""
    if dry_run:
        click.echo(f"would read doc={doc_id} tab={tab_id} format={fmt}")
        return

    try:
        proc = gws_run("docs", "documents", "get",
                       "--params", json.dumps({"documentId": doc_id,
                                               "includeTabsContent": True}))
    except FileNotFoundError as e:
        die(str(e), code=EXIT_SYSTEM, as_json=as_json)
    if proc.returncode != 0:
        die(f"gws docs get failed: {proc.stderr.strip()}",
            code=EXIT_SYSTEM, as_json=as_json)

    doc = json.loads(proc.stdout)
    if fmt == "json":
        text = json.dumps(doc, ensure_ascii=False, indent=2)
    else:
        body = _find_body(doc, tab_id)
        text = _walk_body(body, fmt)

    if str(out) == "-":
        click.echo(text)
    else:
        Path(out).write_text(text, encoding="utf-8")
        if not quiet:
            click.echo(f"wrote {out}")
