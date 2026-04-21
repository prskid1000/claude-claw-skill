# `claw img` — Image Operations Reference

CLI wrapper over Pillow.

## Contents
- [Resize / Fit](#resize-fit) · [Convert](#convert) · [Watermark / Overlay](#watermark-overlay) · [EXIF](#exif)

---

## Resize / Fit
### `resize`
```bash
claw img resize <SRC> --geometry <WxH> --out <OUT> [--force]
```
### `fit`
```bash
claw img fit <SRC> --size <WxH> --out <OUT> [--force]
```

## Convert
### `convert`
```bash
claw img convert <SRC> <OUT> [--force]
```
### `to-webp`
```bash
claw img to-webp <SRC> --out <OUT> [--force]
```

## Watermark / Overlay
### `watermark`
```bash
claw img watermark <SRC> --text <TEXT> --out <OUT> [--force]
```

## EXIF
### `exif`
```bash
claw img exif <SRC> [--json] [--strip] [--out <OUT>]
```

---

## Quick Reference
| Task | Command |
|------|---------|
| Resize | `claw img resize in.png --geometry 800x600 --out out.png` |
| WebP | `claw img to-webp in.png --out out.webp` |
| Strip EXIF | `claw img exif in.jpg --strip --out clean.jpg` |
