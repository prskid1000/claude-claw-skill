# `claw img` — Image Operations Reference

CLI wrapper over Pillow (PIL) for image processing. Handles resizing, format conversion, metadata, and composition.

## Contents

- **TRANSFORM**
  - [Resize](#11-resize) · [Fit](#12-fit) · [Pad](#13-pad) · [Thumbnail](#14-thumb) · [Crop](#15-crop)
- **CONVERT**
  - [Universal Convert](#21-convert) · [To JPEG](#22-to-jpeg) · [To WebP](#23-to-webp)
- **ENHANCE / EDIT**
  - [Watermark](#31-watermark) · [Enhance](#32-enhance) · [Sharpen](#33-sharpen) · [Composite](#34-composite) · [Overlay](#35-overlay)
- **METADATA**
  - [EXIF Operations](#41-exif)
- **BATCH / UTILS**
  - [Rename](#51-rename) · [Batch Process](#52-batch) · [GIF from Frames](#53-gif-from-frames)

---

## Critical Rules

1. **Aspect Ratio** — Use `fit` instead of `resize` to maintain aspect ratio while filling a bounding box.
2. **EXIF Orientation** — `exif --strip` removes orientation flags. Some viewers may display stripped images with incorrect rotation.
3. **Format Support** — WebP and JPEG support require the corresponding system libraries (usually bundled with Pillow wheels).
4. **GIF Optimization** — `gif-from-frames` does not perform heavy compression; ensure input frames are already optimized for web.

---

## 1.1 resize
Change image dimensions to an exact width and height.
```bash
claw img resize <SRC> --geometry <WxH> --out <OUT> [--force]
```

## 1.2 fit
Resize image to fit within a bounding box while preserving aspect ratio.
```bash
claw img fit <SRC> --size <WxH> --out <OUT> [--force]
```

## 1.3 pad
Add padding (borders) to an image.
```bash
claw img pad <SRC> --padding <N> --color <COLOR> --out <OUT> [--force]
```

## 1.4 thumb
Create a small thumbnail version of an image.
```bash
claw img thumb <SRC> --size <WxH> --out <OUT> [--force]
```

## 1.5 crop
Extract a rectangular sub-region from an image.
```bash
claw img crop <SRC> --box <x0,y0,x1,y1> --out <OUT> [--force]
```

---

## 2.1 convert
Universal format converter (supports PNG, JPG, BMP, TIFF, etc.).
```bash
claw img convert <SRC> <OUT> [--force]
```

## 2.2 to-jpeg
Optimized conversion to JPEG with quality controls.
```bash
claw img to-jpeg <SRC> --out <OUT> [--quality 85] [--force]
```

## 2.3 to-webp
Convert to WebP format (supports lossy and lossless).
```bash
claw img to-webp <SRC> --out <OUT> [--lossless] [--force]
```

---

## 3.1 watermark
Apply a text watermark to the image.
```bash
claw img watermark <SRC> --text <TEXT> --out <OUT> [--opacity 0.5] [--force]
```

## 3.2 enhance
Apply tonal corrections. Combine any of `--autocontrast`, `--equalize`, `--posterize`, `--solarize`. Note: there is no `--type`/`--factor`; for brightness/contrast/color enhancement, use ImageMagick directly.
```bash
claw img enhance <SRC> --out <OUT> [--autocontrast] [--cutoff <0-49>] [--equalize] [--posterize <1-8>] [--solarize <0-255>]
```

## 3.3 sharpen
Apply an unsharp mask. Tune via `--radius` (px), `--amount` (percent), `--threshold` (skip low-contrast pixels).
```bash
claw img sharpen <SRC> --out <OUT> [--radius <FLOAT>] [--amount <INT>] [--threshold <INT>]
```

## 3.4 composite
Alpha-composite a foreground image onto a background at pixel offset `x,y`. `--bg` accepts a path OR a color string; `--fg` is a path.
```bash
claw img composite --bg <PATH|COLOR> --fg <FG_PATH> --out <OUT> [--at <X,Y>] [--alpha <0-1>]
```

## 3.5 overlay
Composite a scaled logo onto `BG` at a named corner (TL/TR/BL/BR/center). Logo size is `--scale` × shortest edge of base.
```bash
claw img overlay <BG> --logo <LOGO_PATH> --out <OUT> [--scale <FLOAT>] [--position TL|TR|BL|BR|center] [--padding <PX>] [--margin <PX>]
```

---

## 4.1 exif
Read, write, or strip EXIF metadata.
```bash
claw img exif <SRC> [--json] [--strip] [--set KEY=VAL] [--out <OUT>]
```

---

## 5.1 rename
Bulk rename images based on pattern or date.
```bash
claw img rename <FILES...> --pattern <PATTERN> [--force]
```

## 5.2 batch
Run an op chain on every image in a directory. The chain is a single `--op` string with pipe-separated steps, e.g. `'resize:1024x|strip|webp:85'`.
```bash
claw img batch <DIRECTORY> --op '<step1>|<step2>|...' [--out <DIR>] [--recursive] [--pattern <GLOB>] [--workers <N>] [--stream]
```

## 5.3 gif-from-frames
Create an animated GIF from a sequence of images.
```bash
claw img gif-from-frames <FILES...> --out <OUT_GIF> [--delay MS] [--loop]
```

---

## Footguns
- **Lossy Compression** — Converting JPEG to JPEG repeatedly will degrade quality ("generation loss").
- **Alpha Channel** — Converting RGBA (PNG) to JPEG will lose transparency (usually fills with black or white).

## Escape Hatch
Underlying library: `Pillow` (PIL). For high-performance batch processing, consider `ImageMagick` via shell.

## Quick Reference
| Task | Command |
|------|---------|
| Resize | `claw img resize img.png --geometry 800x600` |
| Preserve Ratio | `claw img fit img.png --size 800x600` |
| Strip Metadata | `claw img exif img.jpg --strip` |
| Convert WebP | `claw img to-webp img.png -o img.webp` |
| Animated GIF | `claw img gif-from-frames frame*.png -o anim.gif` |
