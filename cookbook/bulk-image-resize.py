#!/usr/bin/env python3
"""
Cortex Example: bulk-image-resize
Description: Bulk resize images with format conversion
Tags: image,pillow,resize,batch
Captured: 2026-03-25
Source: bulk-image-resize.py

Usage:
  python ~/.claude/skills/cortex/cookbook/bulk-image-resize.py
"""

#!/usr/bin/env python3
"""
Bulk resize images in a directory. Supports JPEG, PNG, WebP, GIF.
Preserves aspect ratio. Optionally converts format.

Usage:
    python bulk-image-resize.py input_dir output_dir --max-width 800
    python bulk-image-resize.py input_dir output_dir --max-width 1200 --format webp --quality 85
"""

import sys
import argparse
from pathlib import Path
from PIL import Image

SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff"}


def resize_images(input_dir, output_dir, max_width=800, max_height=None, fmt=None, quality=90):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    images = [f for f in input_dir.iterdir() if f.suffix.lower() in SUPPORTED]
    if not images:
        print("No supported images found.")
        return

    print(f"Processing {len(images)} images...")
    for img_path in sorted(images):
        try:
            img = Image.open(img_path)

            # Calculate new size preserving aspect ratio
            w, h = img.size
            if max_height:
                ratio = min(max_width / w, max_height / h)
            else:
                ratio = max_width / w

            if ratio < 1:
                new_size = (int(w * ratio), int(h * ratio))
                img = img.resize(new_size, Image.LANCZOS)

            # Determine output format
            out_ext = f".{fmt}" if fmt else img_path.suffix.lower()
            if out_ext in (".jpg", ".jpeg"):
                out_ext = ".jpg"
                save_fmt = "JPEG"
            elif out_ext == ".png":
                save_fmt = "PNG"
            elif out_ext == ".webp":
                save_fmt = "WEBP"
            elif out_ext == ".gif":
                save_fmt = "GIF"
            else:
                save_fmt = "PNG"
                out_ext = ".png"

            # Convert RGBA to RGB for JPEG
            if save_fmt == "JPEG" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            out_path = output_dir / f"{img_path.stem}{out_ext}"
            img.save(str(out_path), save_fmt, quality=quality, optimize=True)
            print(f"  {img_path.name} ({w}x{h}) → {out_path.name} ({img.size[0]}x{img.size[1]})")

        except Exception as e:
            print(f"  ERROR: {img_path.name}: {e}")

    print(f"\nDone → {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk resize images")
    parser.add_argument("input_dir", help="Input directory")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--max-width", type=int, default=800)
    parser.add_argument("--max-height", type=int, default=None)
    parser.add_argument("--format", choices=["jpg", "png", "webp", "gif"], default=None)
    parser.add_argument("--quality", type=int, default=90)
    args = parser.parse_args()
    resize_images(args.input_dir, args.output_dir, args.max_width, args.max_height, args.format, args.quality)
