# PDF Tools Reference

> **TL;DR: use `claw pdf <verb>` for everything in this file's covered branches.** See [references/claw/pdf.md](claw/pdf.md). This reference keeps the Python library APIs (`PyMuPDF` / `fitz`, `PyPDF2` / `pypdf`, `pdfplumber`, `reportlab`) **only** for the escape-hatch surface `claw pdf` deliberately doesn't wrap — `TextPage` reuse, fine-grained annotation stacks, per-strategy table tuning, OCG / layers, reportlab `Canvas` + PLATYPUS, custom `NumberedCanvas`, bespoke AcroForm authoring.

## Contents

- **Which tool?** — [Quick selection guide](#quick-selection-guide)
- **READ text / images / tables**
  - [PyMuPDF](#1-pymupdf-fitz----pdf-read--edit--render) — [text extraction modes / flags](#13-text-extraction) · [table finder](#14-table-extraction) · [image extraction](#15-image-extraction)
  - [pdfplumber](#3-pdfplumber----pdf-data-extraction) — [positional dicts](#32-page-objects) · [text extraction](#33-text-extraction) · [table tuning](#34-table-extraction) · [visual debug](#35-visual-debugging) · [crop / filter](#36-crop--filter)
- **RENDER pages to images** — [PyMuPDF `page.get_pixmap`](#12-page-rendering)
- **EDIT (annotate / redact / draw / watermark)** — [PyMuPDF annotations](#16-annotations) · [redaction](#17-redaction) · [watermarks & overlays](#110-watermarks--overlays) · [shape drawing](#114-drawing-shape-class) · [TextWriter / Story / insert_htmlbox](#115-textwriter--story) · [OCG / layers](#117-optional-content-layers--ocg)
- **MERGE / SPLIT / ROTATE / ENCRYPT / FORMS**
  - [PyMuPDF page manipulation](#18-page-manipulation) · [merge / split](#19-merge--split) · [forms / widgets](#111-forms-widgets) · [TOC / bookmarks / links](#112-toc--bookmarks--links) · [metadata & encryption](#113-metadata--encryption)
  - [PyPDF2](#2-pypdf2----pdf-merge--split--transform) — [core ops](#21-core-operations) · [page transforms](#22-page-transforms) · [extract](#23-text--image-extraction) · [metadata & security](#24-metadata--security) · [bookmarks & annotations](#25-bookmarks--annotations) · [forms & attachments](#26-forms--attachments) · [viewer prefs](#27-viewer-preferences)
- **CREATE PDF from scratch** — [reportlab](#4-reportlab----pdf-generation) — [Canvas drawing](#41-canvas-drawing) · [PLATYPUS](#42-platypus-page-layout-and-typography-using-scripts) · [fonts](#43-fonts) · [charts](#44-charts-reportlabgraphics) · [barcodes](#45-barcodes) · [AcroForms / encryption / SVG](#46-other-features)
- **OCR scanned PDFs** — [PyMuPDF + Tesseract](#118-ocr-tesseract-integration)
- **Escape-hatch recipes** — [custom Canvas templates, reply-thread annotations, pdfplumber tuning, AcroForm flatten, Story HTML→PDF, CID fonts](#escape-hatch-recipes)

Examples: [examples/pdf-workflows.md](../examples/pdf-workflows.md) · Cross-tool pipelines: [examples/data-pipelines.md](../examples/data-pipelines.md).

---

## Quick Selection Guide

| Task | Best Library | `claw` verb |
|------|-------------|---|
| Generate PDF from scratch | reportlab | `claw pdf from-html` / `from-md` / `qr` / `barcode` |
| Read / extract text | PyMuPDF or pdfplumber | `claw pdf extract-text` |
| Extract tables | pdfplumber (most tunable) / PyMuPDF | `claw pdf extract-tables` |
| Merge / split / rotate / crop | PyMuPDF or pypdf | `claw pdf merge` / `split` / `rotate` / `crop` |
| Annotate | PyMuPDF (most complete) | `claw pdf annotate` |
| Fill form fields | PyMuPDF or pypdf | `claw pdf form-fill` |
| Render pages to images | PyMuPDF | `claw pdf render` |
| Redact content | PyMuPDF | `claw pdf redact` |
| Encrypt / decrypt | PyMuPDF or pypdf | `claw pdf encrypt` / `decrypt` |
| OCR scanned PDFs | PyMuPDF + Tesseract | `claw pdf ocr` |
| Visual debug of extraction | pdfplumber `page.to_image()` | `claw pdf tables-debug` |
| HTML / CSS to PDF | PyMuPDF Story / reportlab PLATYPUS | `claw pdf from-html` |
| Charts in PDF | reportlab.graphics | — (escape hatch) |
| Barcodes / QR | reportlab.graphics.barcode | `claw pdf qr` / `barcode` |
| Watermarks / overlays | PyMuPDF or pypdf | `claw pdf watermark` / `stamp` |

---

## 1. PyMuPDF (fitz) -- PDF Read / Edit / Render

```python
import fitz
```

### 1.1 Document Operations

> `claw pdf info | meta` covers open / save / metadata read — see [claw/pdf.md](claw/pdf.md). Below: API reference for in-memory open, incremental save, save-tuning flags, property accessors.

Open: `fitz.open(path)` · `fitz.open(stream=bytes, filetype="pdf")` · `fitz.open()` (new empty).

Supported input formats: PDF, XPS, OpenXPS, EPUB, MOBI, FB2, CBZ, SVG, PNG, JPEG, BMP, GIF, TIFF, PNM, PGM, PBM, PPM, PAM, JXR, JPX, JP2.

`doc.save()` kwargs:

| Arg | Purpose |
|---|---|
| `incremental=True` | Append-only save (pair with `encryption=fitz.PDF_ENCRYPT_KEEP`) |
| `garbage` | 0-4 (4 = max compaction) |
| `deflate` / `deflate_images` / `deflate_fonts` | Compress streams |
| `clean` | Sanitize content streams |
| `linear=True` | Linearize for web streaming |
| `ascii=True` | ASCII-encode binary |
| `expand` | Decompress: 1=images, 2=fonts, 255=all |

`doc.saveIncr()` = shorthand incremental save to same file.

Document properties: `page_count`, `metadata`, `is_pdf`, `is_encrypted`, `is_closed`, `needs_pass`, `permissions`, `name`, `chapter_count`, `last_location`, `xref_length()`.

### 1.2 Page Rendering

> `claw pdf render` covers common raster output at chosen DPI / zoom / clip — see [claw/pdf.md](claw/pdf.md). Below: full `get_pixmap` kwargs, Matrix construction, Pixmap ops, SVG output.

```python
pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom),
                      dpi=None,                  # overrides matrix if set
                      colorspace=fitz.csRGB,     # csRGB / csGRAY / csCMYK
                      clip=fitz.Rect(x0, y0, x1, y1),
                      alpha=False,
                      annots=True)
```

Matrix constructors: `fitz.Matrix(zoom_x, zoom_y)` · `fitz.Matrix(1, 0, 0, 1, tx, ty)` (translate) · `fitz.Matrix(fitz.Identity)` · combine: `Matrix(zoom, zoom) * Matrix(rotation_degrees)`.

Pixmap save formats (auto-detected from extension): PNG, PNM, PBM, PPM, PAM, PSD, PS. Override: `pix.save(path, output="png")`.

Pixmap ops: `set_dpi(x, y)` · `gamma_with(g)` · `tint_with(black, white)` · `invert_irect(irect)` · `tobytes(output="png")` · `.samples` (raw pixel bytes) · `.width` / `.height` / `.stride` / `.n` (components per pixel) / `.xres` / `.yres` · `.pixel(x, y)` / `.set_pixel(x, y, color)` · `.copy(source_pix, irect)`.

SVG: `page.get_svg_image(matrix=fitz.Identity, text_as_path=True)`.

### 1.3 Text Extraction

> `claw pdf extract-text [--mode plain|blocks|dict|html]` covers all extraction modes — see [claw/pdf.md](claw/pdf.md). Below: mode outputs, flag semantics, `search_for` API, TextPage reuse.

Extraction modes: `page.get_text(mode)` where mode is `"text"`, `"blocks"`, `"words"`, `"dict"`, `"rawdict"`, `"json"`, `"html"`, `"xhtml"`, `"xml"`.

`"blocks"` → list of `(x0, y0, x1, y1, "text", block_no, block_type)`.
`"words"` → list of `(x0, y0, x1, y1, "word", block_no, line_no, word_no)`.

`"dict"` structure:

```
{
  "width": float, "height": float,
  "blocks": [
    {"type": 0,            # 0=text, 1=image
     "bbox": (x0,y0,x1,y1),
     "lines": [
       {"spans": [
          {"size": float, "flags": int, "font": str,
           "color": int, "ascender": float, "descender": float,
           "text": str, "origin": (x,y), "bbox": (x0,y0,x1,y1)}
        ],
        "wmode": 0,        # 0=horizontal, 1=vertical
        "dir": (1, 0),
        "bbox": (x0,y0,x1,y1)}
     ]}
  ]
}
```

Extraction flags (OR together and pass as `flags=`):

| Flag | Effect |
|---|---|
| `TEXT_PRESERVE_LIGATURES` | Keep ligature chars (fi, fl, …) |
| `TEXT_PRESERVE_WHITESPACE` | Keep all whitespace |
| `TEXT_PRESERVE_IMAGES` | Include images in dict / rawdict |
| `TEXT_INHIBIT_SPACES` | Suppress inter-word space insertion |
| `TEXT_DEHYPHENATE` | Join hyphenated line-breaks |
| `TEXT_PRESERVE_SPANS` | Don't merge spans with same formatting |
| `TEXT_MEDIABOX_CLIP` | Clip to MediaBox |

Text search:

```python
results = page.search_for(
    text, clip=None, quads=False, flags=0,
    textpage=None, hit_max=0,         # 0 = unlimited
)   # returns list[Rect | Quad]
```

TextPage reuse (amortize cost across multiple queries on same page):

```python
tp = page.get_textpage(flags=0, clip=None)
text = page.get_text("text", textpage=tp)
results = page.search_for("query", textpage=tp)
```

`get_text` also accepts `sort=True` (blocks top-to-bottom, left-to-right) and `clip=Rect(...)` (sub-region).

### 1.4 Table Extraction

> `claw pdf extract-tables [--strategy lines|lines_strict|text|explicit] [--vlines ...] [--hlines ...]` covers the tuning surface — see [claw/pdf.md](claw/pdf.md). Below: full `find_tables` kwarg surface for cases the CLI's preset flags can't express (see recipe #2).

`page.find_tables(**kwargs)` — TableFinder; `.tables` is the list.

| Kwarg | Default | Purpose |
|---|---|---|
| `strategy` | `"lines"` | `"lines"` / `"lines_strict"` / `"text"` / `"explicit"` |
| `vertical_strategy` / `horizontal_strategy` | — | Override per axis |
| `vertical_lines` / `horizontal_lines` | — | Explicit x / y coords |
| `snap_tolerance`, `snap_x_tolerance`, `snap_y_tolerance` | 3 | Snap nearby lines |
| `join_tolerance`, `join_x_tolerance`, `join_y_tolerance` | 3 | Join nearby segments |
| `edge_min_length` | 3 | Minimum edge length |
| `min_words_vertical` / `min_words_horizontal` | 3 / 1 | Infer boundary threshold (text strategy) |
| `intersection_tolerance` | 3 | Line-intersection tolerance |
| `text_tolerance`, `text_x_tolerance`, `text_y_tolerance` | 3 | Text-strategy tolerances |
| `add_lines` | — | Extra lines `[(x0,y0,x1,y1), ...]` |

Table props: `tabs[0].extract()` (list of lists), `.bbox`, `.header`, `.to_pandas()`, `.col_count`, `.row_count`.

### 1.5 Image Extraction

> `claw pdf extract-images` covers per-page image dump — see [claw/pdf.md](claw/pdf.md). Below: API for manual xref handling, CMYK → RGB conversion, smask detection.

`page.get_images(full=True)` → list of tuples `(xref, smask, width, height, bpc, colorspace, alt_colorspace, name, filter, invoker)`.

`doc.extract_image(xref)` → `{"ext": "png", "smask": int, "width": int, "height": int, "colorspace": int, "cs-name": str, "xres": int, "yres": int, "image": bytes}`.

Build a `Pixmap` from an xref:

```python
pix = fitz.Pixmap(doc, xref)
if pix.n - pix.alpha > 3:           # CMYK → RGB conversion
    pix = fitz.Pixmap(fitz.csRGB, pix)
pix.save("image.png")
```

### 1.6 Annotations

> `claw pdf annotate` covers common markup + shape + freetext — see [claw/pdf.md](claw/pdf.md). Below: full annotation-type catalog, per-type add API, `set_*` modifiers, reply-thread escape hatch (recipe #3).

Annotation-type constants:

| Constant | Name |
|---|---|
| `PDF_ANNOT_TEXT` | Text (sticky note) |
| `PDF_ANNOT_FREE_TEXT` | FreeText |
| `PDF_ANNOT_HIGHLIGHT` | Highlight |
| `PDF_ANNOT_UNDERLINE` | Underline |
| `PDF_ANNOT_STRIKE_OUT` | StrikeOut |
| `PDF_ANNOT_SQUIGGLY` | Squiggly |
| `PDF_ANNOT_CIRCLE` | Circle |
| `PDF_ANNOT_SQUARE` | Square |
| `PDF_ANNOT_LINE` | Line |
| `PDF_ANNOT_POLY_LINE` | PolyLine |
| `PDF_ANNOT_POLYGON` | Polygon |
| `PDF_ANNOT_INK` | Ink (freehand) |
| `PDF_ANNOT_STAMP` | Stamp |
| `PDF_ANNOT_CARET` | Caret |
| `PDF_ANNOT_FILE_ATTACHMENT` | FileAttachment |
| `PDF_ANNOT_REDACT` | Redaction |

Add methods: `add_highlight_annot`, `add_underline_annot`, `add_strikeout_annot`, `add_squiggly_annot` (all take quads or rect); `add_rect_annot`, `add_circle_annot`, `add_line_annot(p1, p2)`, `add_polyline_annot(points)`, `add_polygon_annot(points)`; `add_text_annot(point, text, icon=...)`; `add_freetext_annot(rect, text, fontsize=12, fontname="helv", text_color=(0,0,0), fill_color=(1,1,1), align=fitz.TEXT_ALIGN_LEFT, rotate=0, border_color=None)`; `add_ink_annot(list_of_point_lists)`; `add_stamp_annot(rect, stamp=fitz.STAMP_Approved)`; `add_caret_annot(point)`; `add_file_annot(point, buffer, filename, ufilename=None, desc=None, icon="PushPin")`.

Text annot icon values: `"Note"`, `"Comment"`, `"Help"`, `"Insert"`, `"Key"`, `"NewParagraph"`, `"Paragraph"`.

Stamp names: `STAMP_Approved`, `STAMP_AsIs`, `STAMP_Confidential`, `STAMP_Departmental`, `STAMP_Draft`, `STAMP_Experimental`, `STAMP_Expired`, `STAMP_Final`, `STAMP_ForComment`, `STAMP_ForPublicRelease`, `STAMP_NotApproved`, `STAMP_NotForPublicRelease`, `STAMP_Sold`, `STAMP_TopSecret`.

Modify: `annot.set_colors(stroke=(r,g,b), fill=(r,g,b))` (0-1), `set_border(width, dashes, style, clouds)`, `set_opacity(0-1)`, `set_info(title, content, subject, creationDate, modDate)`, `set_rect(rect)`, `set_popup(rect)`, `set_name(name)`, `set_flags(flags)`, `set_rotation(angle)`, `update(fontsize, fontname, text_color, fill_color, border_color, border_width, rotate)`.

Iterate / delete: `for annot in page.annots(): ...` · `page.delete_annot(annot)`.

### 1.7 Redaction

> `claw pdf redact` covers the common case — see [claw/pdf.md](claw/pdf.md). Below: full API including graphics-removal policy.

```python
annot = page.add_redact_annot(
    quad_or_rect,
    text=None, fontname="helv", fontsize=11, align=fitz.TEXT_ALIGN_LEFT,
    fill=(1, 1, 1), text_color=(0, 0, 0),
    cross_out=True,
)
page.apply_redactions(
    images=fitz.PDF_REDACT_IMAGE_PIXELS,   # _NONE / _REMOVE / _PIXELS
    graphics=fitz.PDF_REDACT_LINE_ART_IF_TOUCHED,   # _NONE / _IF_TOUCHED / _IF_WRAPPED
)   # permanently removes content under redaction areas
```

### 1.8 Page Manipulation

> `claw pdf rotate | crop | split | merge` cover the common ops — see [claw/pdf.md](claw/pdf.md). Below: API for page-box edits and list-based delete.

Page ops: `doc.new_page(pno=-1, width=595, height=842)` · `doc.insert_page(pno, text="", fontsize, fontname, fontfile, color, width, height)` · `doc.delete_page(pno)` · `doc.delete_pages(from_page, to_page)` · `doc.delete_pages([0, 3, 7])` · `doc.move_page(pno, to=-1)` · `doc.copy_page(pno, to=-1)`.

Rotation: `page.set_rotation(0|90|180|270)`.

Page boxes (read as attributes, set with `set_*`): `mediabox` / `cropbox` / `trimbox` / `artbox` / `bleedbox`.

### 1.9 Merge / Split

> `claw pdf merge` / `split` cover the common cases — see [claw/pdf.md](claw/pdf.md). Below: the single underlying primitive (`insert_pdf`) with its full kwarg surface.

```python
doc.insert_pdf(
    src_doc,
    from_page=-1, to_page=-1,        # -1 = first/last
    start_at=-1,                     # insertion point (-1 = end)
    rotate=-1,                       # -1 = keep
    links=True, annots=True,
    show_progress=0,                 # print every N pages
    final=1,                         # 1 = last insert call (optimizes)
)
```

Split = open new empty doc, `insert_pdf(src, from_page=i, to_page=i)`, save.

### 1.10 Watermarks & Overlays

> `claw pdf watermark | stamp | flatten` cover the common cases — see [claw/pdf.md](claw/pdf.md). Three escape-hatch APIs remain for bespoke overlays:

- **`page.show_pdf_page(rect, src_doc, pno=0, keep_proportion=True, overlay=True, oc=0, rotation=0, clip=None)`** — overlay any page from any source PDF (best for vector stamps).
- **Shape-based** — `page.new_shape()` → `insert_text(point, text, fontsize, color, rotate)` → `finish(color, fill, width, opacity)` → `commit(overlay=True)`.
- **TextWriter** — `fitz.TextWriter(page.rect)` → `append(point, text, fontsize, font)` → `write_text(page, opacity, overlay, color)` — most precise control.

### 1.11 Forms (Widgets)

> `claw pdf form-list | form-fill | flatten` cover read / fill / flatten — see [claw/pdf.md](claw/pdf.md). Below: widget-type catalog + escape-hatch for authoring new widgets from scratch.

| Constant | Type |
|---|---|
| `PDF_WIDGET_TYPE_TEXT` | Text field |
| `PDF_WIDGET_TYPE_CHECKBOX` | Checkbox |
| `PDF_WIDGET_TYPE_COMBOBOX` | Combo box |
| `PDF_WIDGET_TYPE_LISTBOX` | List box |
| `PDF_WIDGET_TYPE_RADIOBUTTON` | Radio button |
| `PDF_WIDGET_TYPE_PUSHBUTTON` | Push button |
| `PDF_WIDGET_TYPE_SIGNATURE` | Signature field |

Create a new widget from scratch (escape hatch — `claw` only fills / flattens existing widgets):

```python
widget = fitz.Widget()
widget.field_name = "myfield"
widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
widget.field_value = "default"
widget.rect = fitz.Rect(100, 100, 300, 120)
widget.text_fontsize = 12
widget.text_font = "helv"
widget.text_color = (0, 0, 0)
widget.fill_color = (0.9, 0.9, 0.9)
widget.border_color = (0, 0, 0)
widget.border_width = 1
widget.field_flags = 0             # e.g. fitz.PDF_FIELD_IS_READ_ONLY
widget.choice_values = ["a", "b"]  # combobox/listbox
widget.button_caption = "Click"    # pushbutton
widget.is_signed = False           # signature
page.add_widget(widget)
```

### 1.12 TOC / Bookmarks / Links

> `claw pdf toc | bookmark | layer` cover common TOC read / write — see [claw/pdf.md](claw/pdf.md). Below: outline API, link-kind catalog, and `insert_link` shape.

TOC: `doc.get_toc(simple=True)` → `[[level, title, page], ...]` or `simple=False` → include dest dict. Set: `doc.set_toc(toc_list)`.

Outline walk: `outline = doc.outline` then iterate `outline.next`; each has `.level`, `.title`, `.page`, `.uri`, `.is_open`.

Link kinds: `LINK_NONE=0`, `LINK_GOTO=1` (internal), `LINK_URI=2`, `LINK_LAUNCH=3` (external file), `LINK_NAMED=4`, `LINK_GOTOR=5` (remote PDF).

```python
# URI
page.insert_link({"kind": fitz.LINK_URI,
                  "from": fitz.Rect(100, 100, 200, 120),
                  "uri": "https://example.com"})
# Internal GOTO
page.insert_link({"kind": fitz.LINK_GOTO,
                  "from": fitz.Rect(100, 100, 200, 120),
                  "page": 5, "to": fitz.Point(0, 0), "zoom": 0})
# Named (e.g. "FirstPage" / "LastPage" / "NextPage" / "PrevPage")
page.insert_link({"kind": fitz.LINK_NAMED,
                  "from": fitz.Rect(100, 100, 200, 120),
                  "name": "FirstPage"})
# Remote PDF
page.insert_link({"kind": fitz.LINK_GOTOR,
                  "from": fitz.Rect(100, 100, 200, 120),
                  "file": "other.pdf", "page": 0, "to": fitz.Point(0, 0)})
```

Also: `page.delete_link(link_dict)` · `page.update_link(link_dict)`.

### 1.13 Metadata & Encryption

> `claw pdf meta | encrypt | decrypt` cover the common surface — see [claw/pdf.md](claw/pdf.md). Below: full `save()` encryption kwarg table and XMP metadata API.

Metadata dict keys: `format`, `title`, `author`, `subject`, `keywords`, `creator`, `producer`, `creationDate`, `modDate`, `trapped`, `encryption`. Write via `doc.set_metadata({...})`. Date format: `"D:20240101000000"`.

XMP: `doc.xref_xml_metadata()` returns XMP XML string.

Encryption kwargs for `doc.save()`:

| Arg | Values |
|---|---|
| `encryption` | `PDF_ENCRYPT_RC4_40` / `PDF_ENCRYPT_RC4_128` / `PDF_ENCRYPT_AES_128` / `PDF_ENCRYPT_AES_256` / `PDF_ENCRYPT_KEEP` (preserve existing) |
| `owner_pw` / `user_pw` | Passwords |
| `permissions` | OR of `PDF_PERM_*` flags below |

Permission flags: `PDF_PERM_PRINT`, `PDF_PERM_MODIFY`, `PDF_PERM_COPY`, `PDF_PERM_ANNOTATE`, `PDF_PERM_FORM`, `PDF_PERM_ACCESSIBILITY`, `PDF_PERM_ASSEMBLE`, `PDF_PERM_PRINT_HQ`.

Unlock: `doc.authenticate("password")` (returns permission flags).

### 1.14 Drawing (Shape Class)

Escape hatch — `claw pdf` doesn't expose freeform canvas drawing. Use `page.new_shape()` for vector overlays.

```python
shape = page.new_shape()
shape.draw_line(p1, p2)
shape.draw_rect(rect)
shape.draw_circle(center, radius)
shape.draw_oval(rect)
shape.draw_curve(p1, p2, p3)        # quadratic Bezier
shape.draw_bezier(p1, p2, p3, p4)   # cubic Bezier
shape.draw_squiggle(p1, p2, breadth=2)
shape.draw_zigzag(p1, p2, breadth=2)
shape.draw_polyline(points)
shape.draw_sector(center, point, angle, fullSector=True)
shape.draw_quad(quad)

shape.insert_text(point, text, fontsize=11, fontname="helv", color=(0,0,0), fill=None, rotate=0)
rc = shape.insert_textbox(rect, text, fontsize=11, fontname="helv", color=(0,0,0), fill=None,
                          align=fitz.TEXT_ALIGN_LEFT, rotate=0)
# rc < 0 = overflow; abs(rc) = unused space

shape.finish(color=(0,0,0), fill=None, width=1, dashes=None,
             lineCap=0, lineJoin=0,           # 0=butt/miter, 1=round, 2=square/bevel
             opacity=1, fill_opacity=1, stroke_opacity=1,
             even_odd=False, closePath=True, oc=0)
shape.commit(overlay=True)           # True=foreground, False=background
```

### 1.15 TextWriter & Story

Escape hatch — `claw pdf from-html | from-md` covers the common "compose document" case via pandoc/Story; these APIs are for in-code composition.

**TextWriter** — precise text placement:

```python
tw = fitz.TextWriter(page.rect, opacity=1, color=(0, 0, 0))
tw.append(pos, text, font=fitz.Font("helv"), fontsize=11,
          language=None, right_to_left=False, small_caps=False)
overflow = tw.fill_textbox(rect, text, pos=None, font=fitz.Font("helv"), fontsize=11,
                            align=fitz.TEXT_ALIGN_LEFT, warn=True, right_to_left=False)
tw.write_text(page, overlay=True, morph=None, oc=0, color=None, opacity=None)
```

**Story** (HTML/CSS → PDF with multi-page flow) — see recipe #5. Key API: `fitz.Story(html=..., user_css=...)` · `story.body.add_paragraph().add_span("text", bold=True)` · `fitz.DocumentWriter("out.pdf")` + `begin_page` / `story.place(rect)` / `story.draw(device)` / `end_page` / `close()`.

**insert_htmlbox** (single-rect HTML render):

```python
excess = page.insert_htmlbox(rect, html_string,
                              css=None, archive=None,   # fitz.Archive for images/fonts
                              overlay=True, rotate=0, oc=0, opacity=1, scale_low=0)
```

### 1.16 Font Handling

Escape hatch — `claw` can't register custom fonts. Needed for CJK (see recipe #6) and embedding specific TTF / OTF files.

`fitz.Font(fontname=None, fontfile=None, fontbuffer=None, script=0, language=None, ordering=-1, is_bold=False, is_italic=False, is_serif=True)`.

Base14 names: `"helv"`, `"tiro"`, `"cour"`, `"symb"`, `"zadb"`, plus explicit `"Helvetica"`, `"Times-Roman"`, `"Courier"`, `"Symbol"`, `"ZapfDingbats"` + bold / italic variants.

CJK `ordering`: 0=China-S, 1=China-T, 2=Japan, 3=Korea.

Font introspection: `.name`, `.flags`, `.is_bold`, `.is_italic`, `.is_writable`, `.ascender`, `.descender`, `.glyph_count`, `.text_length(text, fontsize=11)`, `.char_lengths(text, fontsize=11)`, `.glyph_bbox(chr)`, `.has_glyph(chr)`, `.valid_codepoints()`, `.buffer`.

### 1.17 Optional Content (Layers / OCG)

> `claw pdf layer` covers common list / toggle — see [claw/pdf.md](claw/pdf.md). Below: full OCG authoring API for per-layer content gating.

```python
xref = doc.add_ocg(name, config=-1, on=True, intent="View", usage="Artwork")
xref = doc.set_ocmd(ocgs=None,                 # list of OCG xrefs
                    policy="AnyOn",             # "AnyOn" / "AnyOff" / "AllOn" / "AllOff"
                    ve=None)                    # visibility expression
# Assign OC to content:
page.insert_text(point, "Layer text", fontsize=12, oc=ocg_xref)
page.insert_image(rect, filename="image.png", oc=ocg_xref)
page.show_pdf_page(rect, src, pno=0, oc=ocg_xref)
shape.finish(oc=ocg_xref)
# Toggle visibility:
doc.set_layer_ui_config(number, action=0)      # 0=toggle, 1=on, 2=off
layers = doc.layer_ui_configs()
doc.get_layer(-1)
```

### 1.18 OCR (Tesseract Integration)

> `claw pdf ocr` wraps this — see [claw/pdf.md](claw/pdf.md).

```python
tp = page.get_textpage_ocr(flags=0, language="eng", dpi=72, full=False, tessdata=None)
text = page.get_text("text", textpage=tp)
```

`language` accepts Tesseract codes with `+` for multi-language (e.g. `"eng+deu"`). `full=True` OCRs the whole page; `False` only non-text areas.

---

## 2. PyPDF2 -- PDF Merge / Split / Transform

```python
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
```

> This skill standardises on `PyPDF2`. The maintained fork `pypdf` exposes a near-identical API; to switch, `pip install pypdf` and replace `PyPDF2` with `pypdf` in the imports.

### 2.1 Core Operations

> `claw pdf merge | split` wrap merge / split; all page-range syntax flows through — see [claw/pdf.md](claw/pdf.md). Below: PdfReader / PdfWriter / PdfMerger API surface.

Read: `PdfReader(path_or_stream, password=None)` · `.pages` · `len(reader.pages)`.

Write: `PdfWriter()` · `writer.add_page(page)` · `writer.insert_page(page, index=0)` · `writer.add_blank_page(width=612, height=792)` · `writer.write(path_or_stream)` · clone: `PdfWriter(clone_from=reader_or_path)`.

Merge: `PdfMerger()` · `.append(path, pages=(start, end[, step]))` · `.merge(position, path)` · `.write(path)` · `.close()`.

### 2.2 Page Transforms

Page methods: `page.rotate(90|180|270)` · `page.scale(sx, sy)` · `page.scale_to(width, height)` · `page.merge_page(overlay_page)` · `page.merge_transformed_page(page2, transformation)`.

Transformation DSL: `from PyPDF2 import Transformation` · `op = Transformation().rotate(45).scale(1.5).translate(tx=100, ty=50)` · `page.add_transformation(op)`.

Page boxes (read & set): `page.mediabox`, `.cropbox`, `.trimbox`, `.bleedbox`, `.artbox`. Set via `page.cropbox = PyPDF2.generic.RectangleObject([0, 0, 300, 400])`.

### 2.3 Text & Image Extraction

Text: `page.extract_text()` · `page.extract_text(visitor_body=cb, visitor_text=cb, visitor_operand_before=cb)` · `page.extract_text(extraction_mode="layout", layout_mode_space_vertically=True, layout_mode_scale_weight=1.25, layout_mode_strip_rotated=True)`.

Images: `for image in page.images: ...` (each has `.name`, `.data` bytes). Low-level: walk `page["/Resources"]["/XObject"]`.

### 2.4 Metadata & Security

Metadata: `reader.metadata` (DocumentInformation — `.title`, `.author`, `.subject`, `.creator`, `.producer`) · `reader.xmp_metadata` · `writer.add_metadata({"/Title": "...", ...})`.

Decrypt: `reader.decrypt("password")`.

Encrypt via writer:

```python
writer.encrypt(
    user_password="user",
    owner_password="owner",           # None = same as user
    use_128bit=True,                  # False = RC4-40
    permissions_flag=-1,              # -1 = all permissions
    algorithm=None,                   # "RC4-40" / "RC4-128" / "AES-128" / "AES-256" / "AES-256-R5"
)
```

### 2.5 Bookmarks & Annotations

Outlines read: `reader.outline`.

Outline add:

```python
writer.add_outline_item(
    title="Chapter 1", page_number=0, parent=None, before=None,
    color=None, bold=False, italic=False,
    fit="/Fit",               # /Fit /FitH /FitV /FitB /FitBH /FitBV /XYZ /FitR
    is_open=True,
)
```

Annotations:

```python
from PyPDF2.annotations import (
    Text, FreeText, Line, PolyLine, Polygon, Rectangle, Circle,
    Highlight, Underline, Squiggly, StrikeOut, Stamp, Ink, Link,
)
# Highlight(rect=(x1,y1,x2,y2), quad_points=None)
# FreeText(rect=..., text=..., font="Helvetica", font_size="12pt",
#          font_color="000000", border_color="000000", background_color="ffffff")
# Stamp(rect=..., name="Approved")
# Ink(paths=[[(x1,y1),(x2,y2)]], color="ff0000")
# Link(rect=..., url="https://example.com")           # external
# Link(rect=..., target_page_index=3)                  # internal
writer.add_annotation(page_number=0, annotation=annot)
```

### 2.6 Forms & Attachments

> `claw pdf form-list | form-fill` cover read / fill — see [claw/pdf.md](claw/pdf.md). Below: PyPDF2's alternative flatten pattern (recipe #4) and attachment API.

Read: `reader.get_fields()` · `reader.get_form_text_fields()`.

Fill: `writer.update_page_form_field_values(page, {"name": "value", "checkbox1": "/Yes"}, auto_regenerate=True)`.

Attachments: `writer.add_attachment(filename="data.csv", data=b"col1,col2\na,b")`. Reading embedded files requires walking `reader.trailer["/Root"]["/Names"]["/EmbeddedFiles"]`.

### 2.7 Viewer Preferences

Escape hatch — `claw` doesn't wrap viewer preferences.

```python
writer.page_layout = "/SinglePage"
# /SinglePage /OneColumn /TwoColumnLeft /TwoColumnRight /TwoPageLeft /TwoPageRight

writer.page_mode = "/UseOutlines"
# /UseNone /UseOutlines /UseThumbs /FullScreen /UseOC /UseAttachments

writer.viewer_preferences = {
    "/HideToolbar": True, "/HideMenubar": True, "/HideWindowUI": False,
    "/FitWindow": True, "/CenterWindow": True, "/DisplayDocTitle": True,
    "/NonFullScreenPageMode": "/UseNone", "/Direction": "/L2R",
    "/PrintScaling": "/None", "/Duplex": "/Simplex",
    "/PrintPageRange": [0, 4], "/NumCopies": 1,
}
```

---

## 3. pdfplumber -- PDF Data Extraction

```python
import pdfplumber
```

### 3.1 Open & Page Properties

> `claw pdf extract-tables | chars | words` cover text / table output — see [claw/pdf.md](claw/pdf.md). Below: object-model API for escape-hatch data analysis.

Open: `pdfplumber.open(path, password=None)` or `pdfplumber.open(stream)`.

Page attributes: `page_number` (1-based), `width`, `height`, `bbox` = `(x0, top, x1, bottom)`, `mediabox`, `cropbox`, `trimbox`, `artbox`, `bleedbox`.

### 3.2 Page Objects

Each page exposes lists of dicts with positional data:

| Attribute | Dict keys (highlights) |
|---|---|
| `page.chars` | `text`, `fontname`, `size`, `x0`, `y0`, `x1`, `y1`, `top`, `bottom`, `doctop`, `stroking_color`, `non_stroking_color` |
| `page.lines` | `x0`/`y0`/`x1`/`y1`, `width`, `orientation`, `linewidth`, `dash` |
| `page.rects` | `x0`/`y0`/`x1`/`y1`, `fill`, `stroke`, `linewidth` |
| `page.curves` | `points`, bbox, fill/stroke colors |
| `page.images` | bbox, `srcsize`, `name`, `stream`, `colorspace` |
| `page.annots` | annotation dicts |
| `page.hyperlinks` | filtered annots with URI |

### 3.3 Text Extraction

> `claw pdf extract-text`, `claw pdf words`, `claw pdf chars`, `claw pdf search` wrap these — see [claw/pdf.md](claw/pdf.md). Below: full kwarg surface for `extract_text`, `extract_words`, `extract_text_lines`, `search`.

`page.extract_text(**kwargs)`:

| Kwarg | Default | Purpose |
|---|---|---|
| `x_tolerance` / `x_tolerance_ratio` | 3 / None | Max horizontal gap to merge chars |
| `y_tolerance` | 3 | Max vertical gap to merge lines |
| `layout` | False | True = spatial layout mode |
| `layout_width` / `layout_height` / `layout_width_chars` / `layout_height_chars` | 0 | Layout overrides |
| `x_shift` / `y_shift` | 0 | Offsets |
| `x_density` / `y_density` | 7.25 / 13.0 | Chars / lines per point (layout) |
| `use_text_flow` | False | Follow PDF content-stream order |
| `keep_blank_chars` | False | Keep zero-width blanks |
| `extra_attrs` | None | Group chars by additional attributes |
| `split_at_punctuation` | False | `True` or punctuation string |

`page.extract_text_simple(x_tolerance=3, y_tolerance=3)` — fast fallback.

`page.extract_words(**kwargs)` — adds `expand_ligatures=True`, `return_chars=False`. Each word dict: `{"text", "x0", "top", "x1", "bottom", "upright", "direction", "fontname"?, "size"?, ...}`.

`page.extract_text_lines(layout=False, strip=True, return_chars=True, x_tolerance=3, y_tolerance=3)` — each line: `{"text", "x0", "top", "x1", "bottom", "chars": [...]}`.

`page.search(pattern, regex=True, case=True, x_tolerance=3, y_tolerance=3, return_chars=True, return_groups=True, layout=False)` — each result adds `"chars"` and `"groups"` lists.

### 3.4 Table Extraction

> `claw pdf extract-tables` wraps this — see [claw/pdf.md](claw/pdf.md). Below: full `table_settings` surface for bespoke tuning (recipe #2).

`page.find_tables(table_settings={...})` returns a TableFinder.

| Setting | Default | Purpose |
|---|---|---|
| `vertical_strategy` / `horizontal_strategy` | `"lines"` | `"lines"` / `"lines_strict"` / `"text"` / `"explicit"` |
| `explicit_vertical_lines` / `explicit_horizontal_lines` | `[]` | x / y coords or line dicts |
| `snap_tolerance` / `snap_x_tolerance` / `snap_y_tolerance` | 3 | Snap nearby lines |
| `join_tolerance` / `join_x_tolerance` / `join_y_tolerance` | 3 | Join nearby segments |
| `edge_min_length` | 3 | Minimum edge length |
| `min_words_vertical` / `min_words_horizontal` | 3 / 1 | Text-strategy inference threshold |
| `intersection_tolerance` / `intersection_x_tolerance` / `intersection_y_tolerance` | 3 | Intersection tolerance |
| `text_tolerance` / `text_x_tolerance` / `text_y_tolerance` | 3 | Text-strategy tolerances |

Table props: `tables[0].bbox`, `.cells`, `.rows`, `.extract()` (list of lists; None = empty cell). Shortcuts: `page.find_table()`, `page.extract_table()`, `page.extract_tables()`.

Debug overlay: `page.debug_tablefinder(table_settings={})` returns a PageImage.

Strategy selection:

| Strategy | Use when |
|---|---|
| `"lines"` (default) | Visible ruling lines |
| `"lines_strict"` | Only complete intersections |
| `"text"` | Infer from text alignment |
| `"explicit"` | Provide exact line positions |

### 3.5 Visual Debugging

> `claw pdf tables-debug` wraps this — see [claw/pdf.md](claw/pdf.md).

```python
im = page.to_image(resolution=150, antialias=True)
im.draw_line(obj, stroke="red", stroke_width=1)
im.draw_vline(x, stroke="blue")
im.draw_hline(y, stroke="blue")
im.draw_rect(bbox_or_obj, fill=None, stroke="green", stroke_width=1)
im.draw_circle(center_or_obj, radius=5, fill=None, stroke="green")
im.debug_tablefinder(table_settings={})
im.save("debug.png")
```

### 3.6 Crop & Filter

Escape hatch — `claw` doesn't expose crop / predicate filter.

```python
cropped = page.crop((0, 0, page.width/2, page.height))   # left half
filtered = page.within_bbox((x0, top, x1, bottom))
filtered = page.outside_bbox((x0, top, x1, bottom))
filtered = page.filter(lambda obj: obj["object_type"] == "char" and obj["size"] > 12)
filtered.extract_text()
```

---

## 4. reportlab -- PDF Generation

```python
from reportlab.lib.pagesizes import letter, A4, A3, legal, landscape
from reportlab.lib.units import inch, cm, mm, pica
from reportlab.lib.colors import HexColor, Color, black, white, red, blue, green, transparent
from reportlab.lib import colors
```

> `claw pdf from-html | from-md | qr | barcode` cover the "I want a PDF from content" path — see [claw/pdf.md](claw/pdf.md). This section is the escape hatch for freeform Canvas drawing, PLATYPUS flowables, custom NumberedCanvas, AcroForm authoring — all fundamentally Python-class-level features.

### 4.1 Canvas Drawing

```python
from reportlab.pdfgen import canvas
c = canvas.Canvas("output.pdf", pagesize=letter)   # pagesize = (w, h) in pts; 1 inch = 72 pts
```

#### Lines & shapes

`c.line(x1, y1, x2, y2)` · `c.lines([(x1,y1,x2,y2), ...])` · `c.rect(x, y, w, h, stroke=1, fill=0)` · `c.roundRect(x, y, w, h, radius, stroke=1, fill=0)` · `c.circle(cx, cy, r, stroke=1, fill=0)` · `c.ellipse(x1, y1, x2, y2, stroke=1, fill=0)` · `c.wedge(x1, y1, x2, y2, startAng, extent, stroke=1, fill=0)` · `c.arc(x1, y1, x2, y2, startAng, extent)` · `c.bezier(x1, y1, x2, y2, x3, y3, x4, y4)` · `c.grid(xlist, ylist)`.

Path object:

```python
p = c.beginPath()
p.moveTo(x, y); p.lineTo(x, y)
p.curveTo(x1, y1, x2, y2, x3, y3)   # cubic Bezier
p.arcTo(x1, y1, x2, y2, startAng, extent)
p.rect(x, y, w, h); p.ellipse(x, y, w, h); p.circle(x, y, r)
p.close()
c.drawPath(p, stroke=1, fill=0)
c.clipPath(p, stroke=0, fill=0)
```

#### Text

`c.drawString(x, y, text)` (left-aligned baseline) · `c.drawRightString(x, y, text)` · `c.drawCentredString(x, y, text)` · `c.drawAlignedString(x, y, text, pivotChar=".")` (decimal-aligned).

Text object (advanced control):

```python
t = c.beginText(x, y)
t.setFont("Helvetica", 12)
t.setCharSpace(0); t.setWordSpace(0); t.setLeading(14.4)
t.setRise(0)                         # super/subscript offset
t.setHorizScale(100)                 # horizontal scale %
t.setRenderingMode(0)                # 0=fill 1=stroke 2=fill+stroke 3=invisible 4-7=clip
t.textLine("First line"); t.textLines("Line1\nLine2")
t.moveCursor(dx, dy); t.setTextOrigin(x, y)
c.drawText(t)
```

#### Images

```python
c.drawImage(image, x, y, width=None, height=None,
            mask=None,                # "auto" / [r1,r2,g1,g2,b1,b2]
            preserveAspectRatio=False, showBoundary=False,
            anchor="sw")              # c / n / ne / e / se / s / sw / w / nw
c.drawInlineImage(image, x, y, width=None, height=None)
```

Supported: JPEG, PNG, GIF, BMP, TIFF, PIL Image objects.

#### Colors & opacity

- Named: `colors.red` (140+ available).
- Hex: `HexColor("#FF5733")`.
- RGB: `c.setStrokeColorRGB(r, g, b)` / `c.setFillColorRGB(r, g, b)` (0-1 floats).
- CMYK: `c.setStrokeColorCMYK(c, m, y, k)` / `c.setFillColorCMYK(...)`.
- Gray: `c.setStrokeGray(level)` / `c.setFillGray(level)` (0=black, 1=white).
- Alpha: `c.setFillAlpha(0.5)` / `c.setStrokeAlpha(0.5)`.
- Overprint: `c.setFillOverprint(False)` / `c.setStrokeOverprint(False)`.

#### State & transforms

`c.saveState()` / `c.restoreState()` · `c.translate(tx, ty)` · `c.scale(sx, sy)` · `c.rotate(degrees)` (CCW) · `c.skew(alpha, beta)` · `c.transform(a, b, c, d, e, f)` (affine).

#### Line style

`c.setLineWidth(w)` · `c.setLineCap(0|1|2)` (butt/round/projecting) · `c.setLineJoin(0|1|2)` (miter/round/bevel) · `c.setDash([6, 3], 0)` · `c.setMiterLimit(10)`.

#### Page control

`c.showPage()` finalizes current page · `c.save()` writes the PDF · `c.setPageSize(A4)` · `c.setPageRotation(90)`.

### 4.2 PLATYPUS (Page Layout and Typography Using Scripts)

```python
from reportlab.platypus import (
    SimpleDocTemplate, BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Table, TableStyle, Image, Spacer, PageBreak, FrameBreak,
    CondPageBreak, KeepTogether, KeepInFrame, Preformatted, XPreformatted,
    ListFlowable, ListItem, NextPageTemplate, BalancedColumns,
    TableOfContents, SimpleIndex,
)
```

#### Document templates

`SimpleDocTemplate` (single frame): `SimpleDocTemplate("out.pdf", pagesize=letter, topMargin=72, bottomMargin=72, leftMargin=72, rightMargin=72, title="", author="", subject="", creator="", showBoundary=0)` then `doc.build(flowables, onFirstPage=cb, onLaterPages=cb)`.

`BaseDocTemplate` (custom frames / templates) — see recipe #1. `Frame(x, y, w, h, id, leftPadding, rightPadding, topPadding, bottomPadding, showBoundary)` · `PageTemplate(id, frames=[...], onPage=cb, onPageEnd=cb)` · `doc.addPageTemplates([...])`.

onPage callback signature: `def cb(canvas, doc)` with `doc.page` as current page number.

#### Paragraph inline tags

- `<b>`, `<i>`, `<u>`, `<strike>`
- `<a href="url">link</a>`, `<a name="anchor">`
- `<font name="Courier" size="14" color="red">…</font>`
- `<br/>` line break
- `<sub>`, `<super>`
- `<img src="file.png" width="50" height="50" valign="middle"/>`
- `<bullet>` bullet prefix
- `<seq id="name"/>` auto-numbering
- `<greek>`, `<unichar code="0xNNNN"/>`
- `<span>` with style attrs

#### ParagraphStyle kwargs

`name`, `parent`, `fontName`, `fontSize`, `leading` (line height), `alignment` (TA_LEFT / TA_CENTER / TA_RIGHT / TA_JUSTIFY), `leftIndent`, `rightIndent`, `firstLineIndent`, `spaceBefore`, `spaceAfter`, `textColor`, `backColor`, `borderWidth`, `borderColor`, `borderPadding`, `borderRadius`, `wordWrap` (`"CJK"` for CJK), `bulletFontName`, `bulletFontSize`, `bulletIndent`, `bulletColor`, `bulletAnchor`, `bulletText`, `endDots` (TOC dot leader), `splitLongWords`, `underlineWidth`, `strikeWidth`, `underlineColor`, `strikeColor`, `underlineOffset`, `strikeOffset`, `textTransform` (`"uppercase"` / `"lowercase"` / `"capitalize"`), `allowWidows`, `allowOrphans`.

Built-in styles (via `getSampleStyleSheet()`): `Normal`, `BodyText`, `Title`, `Heading1`–`Heading6`, `Italic`, `Code`, `Bullet`, `Definition`, `OrderedList`, `UnorderedList`.

#### Table kwargs

`data` (2D list), `colWidths` (list or None=auto), `rowHeights`, `style`, `splitByRow=1`, `splitInRow=0`, `repeatRows=0` (header rows each page), `repeatCols=0`, `hAlign` (LEFT/CENTER/RIGHT), `vAlign` (TOP/MIDDLE/BOTTOM), `cellStyles`, `cornerRadii=[tl,tr,bl,br]`.

#### TableStyle commands

Cell refs: `(col, row)` 0-based, `-1` = last. Usage: `TableStyle([(cmd, (c0,r0), (c1,r1), *args), ...])`.

| Category | Commands |
|---|---|
| Color | `BACKGROUND`, `TEXTCOLOR`, `ROWBACKGROUNDS` (alternating list), `COLBACKGROUNDS` |
| Alignment | `ALIGN` (LEFT/CENTER/RIGHT/DECIMAL), `VALIGN` (TOP/MIDDLE/BOTTOM) |
| Font | `FONT`, `FONTNAME`, `FONTSIZE`, `LEADING` |
| Borders | `GRID`, `BOX`, `LINEBELOW`, `LINEABOVE`, `LINEBEFORE`, `LINEAFTER` |
| Padding | `TOPPADDING`, `BOTTOMPADDING`, `LEFTPADDING`, `RIGHTPADDING` |
| Layout | `SPAN` (merge), `NOSPLIT`, `ROUNDEDCORNERS [tl,tr,bl,br]` |

#### Other flowables

```python
Image(filename, width=None, height=None, kind="direct", mask="auto", lazy=1, hAlign="CENTER")
# kind: "direct" (points) / "percentage" / "inch" / "cm" / "mm"

Spacer(width, height)
PageBreak()
FrameBreak()                        # move to next frame
CondPageBreak(height)               # page break if less than `height` remaining
KeepTogether(flowables_list)
KeepInFrame(maxWidth, maxHeight, content=[], mode="shrink", mergeSpace=1,
            hAlign="CENTER", vAlign="MIDDLE", fakeWidth=None)
# mode: "error" / "overflow" / "shrink" / "truncate"

Preformatted(text, style, dedent=0, maxLineLength=None, splitChars=None, newLineChars=None)
XPreformatted(text, style)          # like Preformatted, supports XML tags

ListFlowable(items, bulletType="bullet",   # "bullet" / "1" / "a" / "A" / "i" / "I"
             start=None, bulletFontName="Helvetica", bulletFontSize=12,
             bulletDedent=36, bulletDir="ltr", bulletFormat=None, bulletOffsetY=0)

BalancedColumns(flowables, nCols=2, needed=72, spaceBefore=0, spaceAfter=0,
                showBoundary=None, leftPadding=None, rightPadding=None,
                topPadding=None, bottomPadding=None, innerPadding=None,
                name="", endSlack=0.1)

# TOC — register entries via doc.notify("TOCEntry", (level, text, pageNum, key))
toc = TableOfContents()
toc.levelStyles = [ParagraphStyle("TOC1", ...), ParagraphStyle("TOC2", ...)]
index = SimpleIndex(dot=" . ", headers=True)
```

Switch templates mid-doc: `flowables = [NextPageTemplate("TwoColumn"), PageBreak(), ...]`.

### 4.3 Fonts

Base14 fonts (always available): `Helvetica` / `-Bold` / `-Oblique` / `-BoldOblique` · `Times-Roman` / `-Bold` / `-Italic` / `-BoldItalic` · `Courier` / `-Bold` / `-Oblique` / `-BoldOblique` · `Symbol` · `ZapfDingbats`.

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

pdfmetrics.registerFont(TTFont("MyFont", "/path/to/font.ttf"))
pdfmetrics.registerFont(TTFont("MyFont-Bold", "/path/to/font-bold.ttf"))
pdfmetrics.registerFont(TTFont("MyFont-Italic", "/path/to/font-italic.ttf"))
pdfmetrics.registerFont(TTFont("MyFont-BoldItalic", "/path/to/font-bi.ttf"))
pdfmetrics.registerFontFamily("MyFont",
    normal="MyFont", bold="MyFont-Bold",
    italic="MyFont-Italic", boldItalic="MyFont-BoldItalic")
```

CJK fonts (see recipe #6): `UnicodeCIDFont("STSong-Light")` (SC), `"MSung-Light"` (TC), `"HeiseiMin-W3"` (JP), `"HYSMyeongJo-Medium"` (KR).

Font metrics: `pdfmetrics.getFont(name).face` (`.ascent`, `.descent`) · `pdfmetrics.stringWidth(text, fontname, fontsize)`.

### 4.4 Charts (reportlab.graphics)

Escape hatch — `claw` doesn't wrap reportlab charts (use `claw xlsx chart` → export PDF for most cases).

```python
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF, renderSVG
```

Chart classes share the same shape — set `x` / `y` / `width` / `height`, assign `.data` (list of series lists), configure axes via `chart.valueAxis` / `chart.categoryAxis`, then `drawing.add(chart)`.

- **VerticalBarChart / HorizontalBarChart** — `.data` grouped series, `.bars[i].fillColor`, `.barWidth`, `.groupSpacing`, `.barSpacing`. Stacked via `chart.style = "stacked"`. Axis: `valueAxis.valueMin/Max/Step`, `categoryAxis.labels.{boxAnchor,dx,dy,angle}`, `categoryAxis.categoryNames`.
- **HorizontalLineChart** — `.lines[i].{strokeColor,strokeWidth,symbol}`, `.joinedLines = 1`. Use `makeMarker("Circle")` for symbols.
- **Pie / Pie3d** — `.data`, `.labels`, `.slices[i].{popout,fillColor}`, `.sideLabels`, `.simpleLabels`, `Pie3d.perspective`.
- **SpiderChart** — `.data`, `.labels`, `.strands[i].{fillColor,strokeColor}`.
- **Legend** — `.x`, `.y`, `.alignment`, `.colorNamePairs`, `.columnMaximum`, `.fontName`, `.fontSize`. `drawing.add(legend)`.

Render:

```python
renderPDF.drawToFile(drawing, "chart.pdf", "Title")
renderPDF.draw(drawing, canvas, x, y)    # onto existing canvas
renderSVG.drawToFile(drawing, "chart.svg")
from reportlab.graphics import renderPM
renderPM.drawToFile(drawing, "chart.png", fmt="PNG", dpi=150)
```

### 4.5 Barcodes

> `claw pdf qr` / `claw pdf barcode` wrap the common cases — see [claw/pdf.md](claw/pdf.md). Below: reportlab type catalog and API for custom embedding.

1D types: `Code39`, `Extended39`, `Code93`, `Extended93`, `Code128`, `Code128Auto`, `EAN8`, `EAN13`, `UPCA`, `UPCE`, `I2of5` (Interleaved 2 of 5), `ITF`, `MSI`, `Codabar`, `POSTNET`, `USPS_4State` / `FIM`, `Standard39`, `Standard93`.

```python
from reportlab.graphics.barcode import createBarcodeDrawing
bc = createBarcodeDrawing("Code128", value="ABC123",
                          barWidth=0.01*inch, barHeight=0.5*inch, humanReadable=True)
bc.drawOn(c, x, y)
```

QR:

```python
from reportlab.graphics.barcode.qr import QrCodeWidget
qr = QrCodeWidget(value="https://example.com",
                   barLevel="M",     # L=7% / M=15% / Q=25% / H=30% error correction
                   barWidth=2*inch, barHeight=2*inch, barBorder=4,
                   barFillColor=colors.black, barStrokeColor=colors.black, barStrokeWidth=0)
d = Drawing(200, 200); d.add(qr); d.drawOn(c, x, y)
# Shortcut:
qr_drawing = createBarcodeDrawing("QR", value="data", barLevel="H", barBorder=4, width=150, height=150)
```

### 4.6 Other Features

Escape-hatch surface. `claw` doesn't wrap these.

#### Bookmarks, outlines, internal links

```python
c.bookmarkPage("key")
c.addOutlineEntry("Title", "key", level=0, closed=None)
c.bookmarkHorizontalAbsolute("key", top)
c.linkRect("text", "key", (x1,y1,x2,y2), relative=1, thickness=0, color=colors.blue)
c.linkAbsolute("text", "key", (x1,y1,x2,y2))
c.linkURL("https://example.com", (x1,y1,x2,y2), relative=0, thickness=0)
```

#### Page numbers via PLATYPUS

```python
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(7.5*inch, 0.5*inch, f"Page {doc.page}")
    canvas.restoreState()
# Or inline: Paragraph("Page <seq id='page'/>", style)
# Or: canvas.drawString(x, y, "Page %d" % canvas.getPageNumber())
```

For "Page X of Y" totals, subclass `Canvas` — see recipe pattern in [claw/pdf.md § escape-hatch table](claw/pdf.md).

#### Encryption

```python
from reportlab.lib.pdfencrypt import StandardEncryption
enc = StandardEncryption(
    userPassword="user", ownerPassword="owner",
    strength=256,                    # 40 / 128 / 256
    canPrint=1, canModify=0, canCopy=0, canAnnotate=0,
    canFillForms=0, canExtract=0, canAssemble=0, canPrintHighRes=0,
)
c = canvas.Canvas("encrypted.pdf", encrypt=enc)
# or SimpleDocTemplate("encrypted.pdf", encrypt=enc)
```

#### AcroForms (interactive forms) — escape hatch

All `c.acroForm.*()` calls share: `name`, `tooltip`, `x`, `y`, `width`, `height` (or `size` for buttons), `fontName`, `fontSize`, `borderColor`, `fillColor`, `textColor`, `forceBorder`.

| Call | Extra kwargs |
|---|---|
| `textfield` | `value`, `maxlen`, `fieldFlags` ∈ {`readOnly`, `required`, `noExport`, `multiline`, `password`, `fileSelect`, `doNotSpellCheck`, `doNotScroll`, `comb`, `richText`} |
| `checkbox` | `buttonStyle` ∈ {`check`, `circle`, `cross`, `diamond`, `square`, `star`}, `checked` |
| `radio` | `value` (unique per group), `selected`, `buttonStyle` |
| `choice` | `options=[(val, label), ...]`, `value`, `fieldFlags` ∈ {`combo`, `""` (listbox), `combo\|edit`} |
| `listbox` | `options`, `value` (list), `fieldFlags="multiSelect"` |

#### SVG

```python
from svglib.svglib import svg2rlg
drawing = svg2rlg("input.svg")
drawing.width = 400; drawing.height = 300
drawing.scale(0.5, 0.5)
renderPDF.drawToFile(drawing, "from_svg.pdf")
# or renderPDF.draw(drawing, canvas, x, y) — onto canvas
```

---

## Escape-hatch recipes

Things `claw pdf` doesn't wrap — genuinely need the library APIs above.

### 1. Custom reportlab `Canvas` layout with per-page header/footer callback

PLATYPUS documents with a branded header / footer require a `PageTemplate` callback — `claw pdf from-md` can't express this shape:

```python
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph
from reportlab.lib.pagesizes import A4

def chrome(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(36, A4[1] - 24, "Quarterly Report — Confidential")
    canvas.drawRightString(A4[0] - 36, 24, f"Page {doc.page}")
    canvas.restoreState()

doc = BaseDocTemplate("out.pdf", pagesize=A4)
frame = Frame(36, 36, A4[0]-72, A4[1]-72, id="body")
doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=chrome)])
doc.build([Paragraph("Body goes here.")])
```

### 2. pdfplumber table tuning — merged-cell invoice scans

Default strategies miss tables with invisible separators + merged cells. Tune `text_tolerance` + `intersection_tolerance` + explicit lines:

```python
import pdfplumber
with pdfplumber.open("invoice.pdf") as pdf:
    page = pdf.pages[0]
    table = page.find_tables(table_settings={
        "vertical_strategy": "text",
        "horizontal_strategy": "lines",
        "snap_tolerance": 5,
        "intersection_tolerance": 8,
        "text_tolerance": 2,
        "explicit_vertical_lines": [50, 140, 320, 420, 540],
    })[0].extract()
```

### 3. PyMuPDF reply-thread annotations

A review stack with popups + reply threads — not wrappable via flags:

```python
import fitz
doc = fitz.open("manuscript.pdf")
page = doc[0]
parent = page.add_text_annot((72, 72), "Tighten wording?", icon="Comment")
parent.set_info(title="Reviewer A")
parent.update()
reply = page.add_text_annot((72, 90), "Agreed — will redraft.", icon="Comment")
reply.set_info(title="Reviewer B")
reply._irt_xref = parent.xref        # /IRT = In Reply To
reply.update()
doc.saveIncr()
```

### 4. AcroForm-signed fill + flatten with `pypdf`

Fill in reportlab (adds fields), sign externally, flatten via pypdf by setting the read-only field flag:

```python
from PyPDF2 import PdfReader, PdfWriter, generic
reader = PdfReader("filled.pdf")
writer = PdfWriter(clone_from=reader)
for page in writer.pages:
    for annot in page.get("/Annots", []):
        a = annot.get_object()
        if a.get("/Subtype") == "/Widget":
            a[generic.NameObject("/Ff")] = generic.NumberObject(1)   # read-only
writer.write("flattened.pdf")
```

### 5. PyMuPDF `Story` — HTML/CSS → PDF with multi-page flow

The escape hatch for "I want HTML+CSS without LaTeX / weasyprint":

```python
import fitz
story = fitz.Story(html=open("report.html").read(),
                   user_css="h1 { color: #036; } table td { padding: 4px; }")
wr = fitz.DocumentWriter("report.pdf")
while True:
    dev = wr.begin_page(fitz.paper_rect("a4"))
    more, _ = story.place(fitz.Rect(56, 56, 539, 786))
    story.draw(dev)
    wr.end_page()
    if not more: break
wr.close()
```

### 6. CID fonts for CJK in reportlab

CJK doesn't work with Base14; register a `UnicodeCIDFont` before drawing:

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))   # Japanese
c.setFont("HeiseiMin-W3", 12)
c.drawString(72, 720, "こんにちは世界")
```
