"""claw doctor — environment diagnostics. See references/claw/doctor.md."""

from __future__ import annotations

import importlib
import json
import shutil
import sys

import click


PACKAGES = [
    "openpyxl", "docx", "pptx", "fitz", "pypdf", "pdfplumber", "reportlab",
    "PIL", "lxml", "bs4", "trafilatura", "httpx", "click", "networkx", "yaml",
]

CLI_TOOLS = [
    ("pandoc",   "winget install JohnMacFarlane.Pandoc"),
    ("ffmpeg",   "winget install Gyan.FFmpeg"),
    ("ffprobe",  "(ships with ffmpeg)"),
    ("magick",   "winget install ImageMagick.ImageMagick"),
    ("qpdf",     "winget install qpdf.qpdf"),
    ("tesseract", "winget install UB-Mannheim.TesseractOCR"),
    ("exiftool", "winget install OliverBetz.ExifTool"),
    ("gws",      "npm install -g @anthropic/gws"),
    ("clickup",  "https://github.com/triptechtravel/clickup-cli/releases"),
]


@click.command()
@click.option("--json", "as_json", is_flag=True, help="Emit JSON report.")
@click.option("--scope", type=click.Choice(["all", "packages", "cli", "gws"]), default="all")
def doctor(as_json: bool, scope: str) -> None:
    """Check external dependencies and auth. Exit code 0=all ok, 3=warnings, 4=failures."""
    result: dict = {"packages": [], "cli": [], "summary": {"pass": 0, "warn": 0, "fail": 0}}

    if scope in ("all", "packages"):
        for name in PACKAGES:
            try:
                mod = importlib.import_module(name)
                ver = getattr(mod, "__version__", "?")
                result["packages"].append({"name": name, "status": "pass", "version": ver})
                result["summary"]["pass"] += 1
            except ImportError:
                result["packages"].append({"name": name, "status": "fail",
                                            "hint": f"pip install {name}"})
                result["summary"]["fail"] += 1

    if scope in ("all", "cli"):
        for tool, hint in CLI_TOOLS:
            path = shutil.which(tool)
            if path:
                result["cli"].append({"name": tool, "status": "pass", "path": path})
                result["summary"]["pass"] += 1
            else:
                result["cli"].append({"name": tool, "status": "fail", "hint": hint})
                result["summary"]["fail"] += 1

    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo("claw doctor")
        click.echo("───────────")
        for row in result["packages"]:
            icon = "[✓]" if row["status"] == "pass" else "[✗]"
            extra = row.get("version", "") or row.get("hint", "")
            click.echo(f"  {icon} {row['name']:15s} {extra}")
        click.echo()
        for row in result["cli"]:
            icon = "[✓]" if row["status"] == "pass" else "[✗]"
            extra = row.get("path", "") or f"install: {row.get('hint', '')}"
            click.echo(f"  {icon} {row['name']:15s} {extra}")
        s = result["summary"]
        click.echo(f"\nSummary: {s['pass']} pass · {s['warn']} warn · {s['fail']} fail")

    if result["summary"]["fail"]:
        sys.exit(4)
    if result["summary"]["warn"]:
        sys.exit(3)
