# `claw pdf` — PDF Operations Reference

CLI wrapper over PyMuPDF (fitz), pypdf, and pdfplumber.

## Contents

- **CREATE**
  - [From HTML](#from-html) · [From Markdown](#from-md) · [QR Code](#qr) · [Barcode](#barcode)
- **READ / EXTRACT**
  - [Text](#extract-text) · [Tables](#extract-tables) · [Images](#extract-images) · [Metadata](#meta) · [Search](#search)
- **EDIT / TRANSFORM**
  - [Merge](#merge) · [Split](#split) · [Rotate](#rotate) · [Crop](#crop) · [Render to Image](#render)
- **SECURITY / ANNOTATE**
  - [Watermark](#watermark) · [Redact](#redact) · [Encrypt/Decrypt](#encrypt-decrypt) · [Annotate](#annotate) · [Flatten](#flatten)

---

## 1. CREATE

### `from-html`
```bash
claw pdf from-html <SRC_HTML> <OUT_PDF> [--force]
```

### `from-md`
```bash
claw pdf from-md <SRC_MD> <OUT_PDF> [--force]
```

### `qr`
```bash
claw pdf qr --value <TEXT> -o <OUT_PDF> [--force]
```

### `barcode`
```bash
claw pdf barcode --type <TYPE> --value <TEXT> -o <OUT_PDF> [--force]
```

---

## 2. READ / EXTRACT

### `extract-text`
```bash
claw pdf extract-text <SRC_PDF> [--json]
```

### `extract-tables`
```bash
claw pdf extract-tables <SRC_PDF> [--json]
```

### `info`
```bash
claw pdf info <SRC_PDF> [--json]
```

### `search`
```bash
claw pdf search <SRC_PDF> --term <TEXT> [--json]
```

---

## 3. EDIT / TRANSFORM

### `merge`
```bash
claw pdf merge <INPUTS...> -o <OUT_PDF> [--force]
```

### `split`
```bash
claw pdf split <SRC_PDF> --out-dir <DIR> [--per-page] [--force]
```

### `rotate`
```bash
claw pdf rotate <SRC_PDF> --by <DEGREES> -o <OUT_PDF> [--force]
```

### `crop`
```bash
claw pdf crop <SRC_PDF> --box <x0,y0,x1,y1> -o <OUT_PDF> [--force]
```

### `render`
```bash
claw pdf render <SRC_PDF> --page <N> -o <OUT_IMAGE> [--force]
```

---

## 4. SECURITY / ANNOTATE

### `watermark`
```bash
claw pdf watermark <SRC_PDF> --text <TEXT> -o <OUT_PDF> [--force]
```

### `redact`
```bash
claw pdf redact <SRC_PDF> --regex <PATTERN> -o <OUT_PDF> [--force]
```

### `encrypt` / `decrypt`
```bash
claw pdf encrypt <SRC_PDF> --password <PW> -o <OUT_PDF> [--force]
claw pdf decrypt <SRC_PDF> --password <PW> -o <OUT_PDF> [--force]
```

---

## Quick Reference
| Task | Command |
|------|---------|
| Extract Text | `claw pdf extract-text f.pdf` |
| Merge PDFs | `claw pdf merge a.pdf b.pdf -o out.pdf` |
| QR Code PDF | `claw pdf qr --value "https://..." -o qr.pdf` |
| Rotate PDF | `claw pdf rotate f.pdf --by 90 -o rot.pdf` |
| Render Page | `claw pdf render f.pdf --page 1 -o p1.png` |
