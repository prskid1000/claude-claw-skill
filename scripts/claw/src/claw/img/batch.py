"""claw img batch — op chain over a directory."""

from __future__ import annotations

import io
from pathlib import Path

import click

from claw.common import (
    EXIT_INPUT, Geometry, common_output_options, die, emit_json, safe_write,
)


DEFAULT_PATTERNS = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.tif", "*.tiff", "*.heic")


def _apply_op(img, op: str):
    from PIL import Image, ImageFilter, ImageOps
    name, _, arg = op.partition(":")
    name = name.strip().lower()
    if name == "resize":
        geo = Geometry.parse(arg)
        w, h = geo.apply_to(img.width, img.height)
        return img.resize((max(1, w), max(1, h)), Image.LANCZOS), "image"
    if name == "fit":
        w, h = (int(v) for v in arg.lower().split("x", 1))
        return ImageOps.fit(img, (w, h), method=Image.LANCZOS), "image"
    if name == "thumb":
        m = int(arg)
        copy = img.copy()
        copy.thumbnail((m, m), Image.LANCZOS, reducing_gap=3.0)
        return copy, "image"
    if name == "sharpen":
        parts = [float(p) for p in arg.split(",")] if arg else [2, 150, 3]
        r, a, t = (parts + [2, 150, 3])[:3]
        return img.filter(ImageFilter.UnsharpMask(radius=r, percent=int(a), threshold=int(t))), "image"
    if name == "autocontrast":
        return ImageOps.autocontrast(img, cutoff=1), "image"
    if name == "rotate" and arg.strip().lower() == "auto":
        return ImageOps.exif_transpose(img), "image"
    if name == "strip":
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        return clean, "image"
    if name == "jpeg":
        q = int(arg) if arg else 85
        return img, ("JPEG", {"quality": q})
    if name == "webp":
        q = int(arg) if arg else 85
        return img, ("WEBP", {"quality": q})
    if name == "png":
        return img, ("PNG", {})
    raise click.UsageError(f"unknown op: {name}")


@click.command(name="batch")
@click.argument("directory", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--op", "ops", required=True, help="Op chain: 'resize:1024x|strip|webp:85'")
@click.option("--out", "out_dir", default=None, type=click.Path(path_type=Path))
@click.option("--recursive", is_flag=True)
@click.option("--pattern", default=None, help="Glob pattern (default: common image exts).")
@click.option("--stream", is_flag=True, help="Emit one JSON line per file.")
@common_output_options
def batch(directory: Path, ops: str, out_dir: Path | None, recursive: bool,
          pattern: str | None, stream: bool,
          force: bool, backup: bool, as_json: bool, dry_run: bool,
          quiet: bool, verbose: bool, mkdir: bool) -> None:
    """Run an op chain on every image in <dir>."""
    try:
        from PIL import Image
    except ImportError:
        die("Pillow not installed", code=EXIT_INPUT,
            hint="uv tool install 'claw[img]'", as_json=as_json)

    patterns = [pattern] if pattern else list(DEFAULT_PATTERNS)
    files: list[Path] = []
    for pat in patterns:
        files.extend(directory.rglob(pat) if recursive else directory.glob(pat))
    files = [f for f in sorted(set(files)) if f.is_file()]

    op_list = [o.strip() for o in ops.split("|") if o.strip()]
    results: list[dict] = []
    for f in files:
        save_fmt = None
        save_kwargs: dict = {}
        if dry_run:
            results.append({"src": str(f), "ops": op_list, "planned": True})
            if stream:
                emit_json(results[-1])
            continue
        img = Image.open(f)
        for op in op_list:
            img, kind = _apply_op(img, op)
            if kind != "image":
                save_fmt, save_kwargs = kind
        if save_fmt is None:
            save_fmt = img.format or "PNG"
        target_ext = f".{save_fmt.lower()}" if save_fmt != "JPEG" else ".jpg"
        dst = (out_dir / f.relative_to(directory)).with_suffix(target_ext) \
            if out_dir else f.with_suffix(target_ext)
        buf = io.BytesIO()
        img.save(buf, format=save_fmt, **save_kwargs)
        safe_write(dst, lambda fp, b=buf: fp.write(b.getvalue()),
                   force=force or (dst == f), backup=backup, mkdir=True)
        rec = {"src": str(f), "dst": str(dst)}
        results.append(rec)
        if stream:
            emit_json(rec)

    if not stream and as_json:
        emit_json({"count": len(results), "items": results})
    elif not stream and not quiet:
        click.echo(f"processed {len(results)} file(s)")
