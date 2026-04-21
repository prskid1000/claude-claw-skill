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
Adjust brightness, contrast, color, or sharpness.
```bash
claw img enhance <SRC> --type <brightness|contrast|color> --factor <FLOAT> --out <OUT> [--force]
```

## 3.3 sharpen
Apply a sharpening filter to the image.
```bash
claw img sharpen <SRC> --out <OUT> [--factor <FLOAT>] [--force]
```

## 3.4 composite
Combine two images using an alpha mask or blending mode.
```bash
claw img composite <BASE> <OVERLAY> --out <OUT> [--force]
```

## 3.5 overlay
Simple overlay of one image onto another at a specific position.
```bash
claw img overlay <BASE> <OVERLAY> --pos <X,Y> --out <OUT> [--force]
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
Apply a set of operations to multiple images in one pass.
```bash
claw img batch <FILES...> --ops <RESIZE,CONVERT,...> --out-dir <DIR>
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

## Quick Reference Table
| Task | Command |
|------|---------|
| Resize | `claw img resize img.png --geometry 800x600` |
| Preserve Ratio | `claw img fit img.png --size 800x600` |
| Strip Metadata | `claw img exif img.jpg --strip` |
| Convert WebP | `claw img to-webp img.png -o img.webp` |
| Animated GIF | `claw img gif-from-frames frame*.png -o anim.gif` |
