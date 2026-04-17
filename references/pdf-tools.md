# PDF Tools Reference

> **TL;DR: use `claw pdf <verb>` for common tasks.** See [references/claw/pdf.md](claw/pdf.md). This reference documents the Python library APIs (`PyMuPDF`, `PyPDF2`/`pypdf`, `pdfplumber`, `reportlab`) for escape-hatch / advanced workflows not covered by `claw pdf` — custom `reportlab.Canvas` layouts, bespoke annotation stacks, fine-grained pdfplumber table tuning, `TextPage` reuse, OCR integration, XMP metadata, layer / OCG authoring.

## Contents

- **Which tool?** — [Quick selection guide (capability matrix)](#quick-selection-guide) *(keep — decision-guide content `claw` does not replace)*
- **READ text / images / tables** *(common cases covered by `claw pdf extract-text/extract-tables/extract-images`)*
  - [PyMuPDF (fitz): extraction modes, TextPage reuse, search, image extract, table find](#1-pymupdf-fitz----pdf-read--edit--render)
  - [pdfplumber: positional data, crop, within_bbox, table tuning](#3-pdfplumber----pdf-data-extraction)
- **RENDER pages to images** — PyMuPDF `get_pixmap` *(covered by `claw pdf render`)*
- **EDIT (annotate / redact / draw / watermark)** — PyMuPDF *(`claw pdf watermark/stamp/redact` covers the common cases; annotation-stack authoring stays here)*
- **MERGE / SPLIT / ROTATE / ENCRYPT / FORMS** *(covered by `claw pdf merge/split/rotate/encrypt/form-fill`)*
  - [PyMuPDF merge/split, encryption, TOC, links](#19-merge--split)
  - [PyPDF2 core ops, transforms, bookmarks, annotations, forms](#2-pypdf2----pdf-merge--split--transform)
- **CREATE PDF from scratch** — `reportlab` *(simple HTML/MD → PDF covered by `claw convert` and `claw pdf from-html/from-md`; `Canvas` + PLATYPUS stay here)*
  - [Canvas drawing, PLATYPUS flowables, fonts, charts, barcodes, AcroForms](#4-reportlab----pdf-generation)
- **OCR scanned PDFs** — PyMuPDF + Tesseract *(covered by `claw pdf ocr`)*
- **Escape-hatch recipes** — [custom Canvas templates, per-annotation replies, pdfplumber tuning, AcroForm auth, Story HTML→PDF, CID fonts](#escape-hatch-recipes)

Examples: [examples/pdf-workflows.md](../examples/pdf-workflows.md) · Cross-tool pipelines (PDF → tables → Excel, etc.): [examples/data-pipelines.md](../examples/data-pipelines.md).

## 1. PyMuPDF (fitz) -- PDF Read / Edit / Render

```python
import fitz  # PyMuPDF
```

### 1.1 Document Operations

#### Open a document

```python
doc = fitz.open(filename)          # PDF, XPS, EPUB, MOBI, FB2, CBZ, SVG, images
doc = fitz.open(stream=bytes_data, filetype="pdf")  # from memory
doc = fitz.open()                  # create new empty PDF
```

Supported formats: PDF, XPS, OpenXPS, EPUB, MOBI, FB2, CBZ, SVG, PNG, JPEG, BMP, GIF, TIFF, PNM, PGM, PBM, PPM, PAM, JXR, JPX, JP2.

#### Save

```python
doc.save(filename)                 # save to new file
doc.save(filename, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)  # incremental save
doc.saveIncr()                     # shorthand incremental save (same file)
doc.save(filename,
    garbage=4,                     # garbage collection level 0-4 (4 = max compaction)
    deflate=True,                  # compress streams
    deflate_images=True,           # compress image streams
    deflate_fonts=True,            # compress font streams
    clean=True,                    # sanitize content streams
    linear=True,                   # linearize for web
    pretty=False,                  # pretty-print objects
    ascii=False,                   # ASCII-encode binary data
    expand=0,                      # decompress: 1=images, 2=fonts, 255=all
    no_new_id=False,               # suppress new file ID
)
```

#### Properties

```python
doc.page_count                     # number of pages
doc.metadata                       # dict: format, title, author, subject, keywords, creator, producer, creationDate, modDate, trapped, encryption
doc.is_pdf                         # True if PDF
doc.is_encrypted                   # True if encrypted
doc.is_closed                      # True if closed
doc.needs_pass                     # True if password required
doc.permissions                    # access permissions int
doc.name                           # filename
doc.chapter_count                  # number of chapters (EPUB)
doc.last_location                  # (chapter, page) of last page
doc.xref_length()                  # total number of PDF objects
```

#### Close

```python
doc.close()
```

---

### 1.2 Page Rendering

#### Pixmap (raster)

```python
page = doc[page_number]            # 0-based
pix = page.get_pixmap(
    matrix=fitz.Matrix(zoom, zoom),  # zoom factor (2 = 200%)
    dpi=None,                      # override resolution (default 72); overrides matrix
    colorspace=fitz.csRGB,         # fitz.csRGB, fitz.csGRAY, fitz.csCMYK
    clip=fitz.Rect(x0, y0, x1, y1),  # render sub-region only
    alpha=False,                   # include alpha channel
    annots=True,                   # render annotations
)
```

**Matrix constructors:**

```python
fitz.Matrix(zoom_x, zoom_y)       # scale
fitz.Matrix(1, 0, 0, 1, tx, ty)   # translate
fitz.Matrix(fitz.Identity)         # identity
mat = fitz.Matrix(zoom, zoom) * fitz.Matrix(rotation_degrees)  # combine zoom + rotation
```

#### Pixmap operations

```python
pix.save(filename)                 # auto-detect format from extension: PNG, PNM, PBM, PPM, PAM, PSD, PS
pix.save(filename, output="png")   # explicit format
pix.set_dpi(x_dpi, y_dpi)         # set DPI metadata
pix.gamma_with(gamma)             # apply gamma correction (float, 1.0 = no change)
pix.tint_with(black, white)       # tint: black/white are ints (sRGB)
pix.invert_irect(irect)           # invert colors within sub-rectangle
pix.tobytes(output="png")         # return bytes: png, pnm, pbm, ppm, pam, psd, ps
pix.samples                       # raw pixel bytes
pix.width, pix.height             # dimensions
pix.stride                        # bytes per row
pix.n                             # components per pixel
pix.xres, pix.yres                # resolution
pix.pixel(x, y)                   # single pixel tuple
pix.set_pixel(x, y, color)        # set single pixel
pix.copy(source_pix, irect)       # copy from another pixmap
```

#### SVG rendering

```python
svg_text = page.get_svg_image(
    matrix=fitz.Identity,          # transformation matrix
    text_as_path=True,             # True: text as paths; False: text as <text> elements
)
```

---

### 1.3 Text Extraction

#### Extraction modes

```python
text = page.get_text("text")       # plain text (default)
blocks = page.get_text("blocks")   # list of (x0, y0, x1, y1, "text", block_no, block_type)
words = page.get_text("words")     # list of (x0, y0, x1, y1, "word", block_no, line_no, word_no)
d = page.get_text("dict")          # full structure: blocks > lines > spans with font/color/size/flags
d = page.get_text("rawdict")       # like dict but chars instead of text in spans
j = page.get_text("json")          # JSON string of dict output
html = page.get_text("html")       # HTML with styling
xhtml = page.get_text("xhtml")     # XHTML
xml = page.get_text("xml")         # XML with char-level detail
```

**"dict" structure:**

```
{
  "width": float, "height": float,
  "blocks": [
    {
      "type": 0,  # 0=text, 1=image
      "bbox": (x0, y0, x1, y1),
      "lines": [
        {
          "spans": [
            {
              "size": float, "flags": int, "font": str,
              "color": int,  # sRGB, e.g. 0x000000
              "ascender": float, "descender": float,
              "text": str, "origin": (x, y),
              "bbox": (x0, y0, x1, y1),
            }
          ],
          "wmode": 0,  # 0=horizontal, 1=vertical
          "dir": (1, 0),  # writing direction
          "bbox": (x0, y0, x1, y1),
        }
      ]
    }
  ]
}
```

#### Extraction flags

Pass via `flags` parameter to `get_text()`:

```python
page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE | fitz.TEXT_PRESERVE_LIGATURES)
```

| Flag | Effect |
|------|--------|
| `TEXT_PRESERVE_LIGATURES` | Keep ligature characters (fi, fl, etc.) |
| `TEXT_PRESERVE_WHITESPACE` | Preserve all whitespace characters |
| `TEXT_PRESERVE_IMAGES` | Include images in "dict"/"rawdict" output |
| `TEXT_INHIBIT_SPACES` | Suppress inter-word space insertion |
| `TEXT_DEHYPHENATE` | Remove hyphens at line breaks and join words |
| `TEXT_PRESERVE_SPANS` | Do not merge adjacent spans with same formatting |
| `TEXT_MEDIABOX_CLIP` | Clip text to page MediaBox |

#### Text search

```python
results = page.search_for(
    text,                          # search string
    clip=None,                     # restrict to Rect
    quads=False,                   # True: return Quad list; False: return Rect list
    flags=0,                       # TEXT_* flags
    textpage=None,                 # reuse existing TextPage
    hit_max=0,                     # max results (0 = unlimited)
)
# returns list of Rect or Quad objects marking each occurrence
```

#### TextPage reuse

```python
tp = page.get_textpage(flags=0, clip=None)
text = page.get_text("text", textpage=tp)
results = page.search_for("query", textpage=tp)
```

#### Sort parameter

```python
page.get_text("text", sort=True)   # sort blocks top-to-bottom, left-to-right
```

#### Clip parameter

```python
page.get_text("text", clip=fitz.Rect(0, 0, 300, 400))  # extract from sub-region
```

---

### 1.4 Table Extraction

```python
tabs = page.find_tables(
    clip=None,                     # restrict to Rect
    strategy="lines",              # "lines", "lines_strict", "text", "explicit"
    vertical_strategy=None,        # override strategy for verticals
    horizontal_strategy=None,      # override strategy for horizontals
    vertical_lines=None,           # explicit vertical line x-coordinates
    horizontal_lines=None,         # explicit horizontal line y-coordinates
    snap_tolerance=3,              # snap nearby lines
    snap_x_tolerance=None,
    snap_y_tolerance=None,
    join_tolerance=3,              # join nearby line segments
    join_x_tolerance=None,
    join_y_tolerance=None,
    edge_min_length=3,             # minimum edge length
    min_words_vertical=3,          # min words to infer vertical line
    min_words_horizontal=1,        # min words to infer horizontal line
    intersection_tolerance=3,      # tolerance for line intersections
    text_tolerance=3,              # tolerance for text-based strategy
    text_x_tolerance=None,
    text_y_tolerance=None,
    add_lines=None,                # additional lines [(x0,y0,x1,y1), ...]
)
# tabs.tables -> list of Table objects
# tabs[0].extract() -> list of lists (row data)
# tabs[0].bbox -> bounding box Rect
# tabs[0].header -> Header object
# tabs[0].to_pandas() -> pandas DataFrame
# tabs[0].col_count, tabs[0].row_count
```

---

### 1.5 Image Extraction

```python
# List images on page: (xref, smask, width, height, bpc, colorspace, alt. colorspace, name, filter, invoker)
images = page.get_images(full=True)

# Extract image by xref
img = doc.extract_image(xref)
# returns dict: {"ext": "png", "smask": int, "width": int, "height": int, "colorspace": int, "cs-name": str, "xres": int, "yres": int, "image": bytes}

# Create Pixmap from xref
pix = fitz.Pixmap(doc, xref)
pix.save("image.png")

# Handle CMYK / SMask
if pix.n - pix.alpha > 3:         # CMYK
    pix = fitz.Pixmap(fitz.csRGB, pix)  # convert to RGB
```

---

### 1.6 Annotations

#### 16 annotation types

| Type constant | Name |
|---------------|------|
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

#### Add annotations

```python
# Markup annotations (highlight, underline, strikeout, squiggly)
annot = page.add_highlight_annot(quads_or_rect)
annot = page.add_underline_annot(quads_or_rect)
annot = page.add_strikeout_annot(quads_or_rect)
annot = page.add_squiggly_annot(quads_or_rect)

# Shape annotations
annot = page.add_rect_annot(rect)
annot = page.add_circle_annot(rect)
annot = page.add_line_annot(p1, p2)
annot = page.add_polyline_annot(points)
annot = page.add_polygon_annot(points)

# Text annotations
annot = page.add_text_annot(point, text, icon="Note")
# icons: "Note", "Comment", "Help", "Insert", "Key", "NewParagraph", "Paragraph"
annot = page.add_freetext_annot(rect, text, fontsize=12, fontname="helv", text_color=(0,0,0), fill_color=(1,1,1), align=fitz.TEXT_ALIGN_LEFT, rotate=0, border_color=None)

# Other
annot = page.add_ink_annot(list_of_point_lists)
annot = page.add_stamp_annot(rect, stamp=fitz.STAMP_Approved)
# stamps: STAMP_Approved, STAMP_AsIs, STAMP_Confidential, STAMP_Departmental, STAMP_Draft, STAMP_Experimental, STAMP_Expired, STAMP_Final, STAMP_ForComment, STAMP_ForPublicRelease, STAMP_NotApproved, STAMP_NotForPublicRelease, STAMP_Sold, STAMP_TopSecret
annot = page.add_caret_annot(point)
annot = page.add_file_annot(point, buffer, filename, ufilename=None, desc=None, icon="PushPin")
```

#### Modify annotations

```python
annot.set_colors(stroke=(1,0,0), fill=(1,1,0))  # RGB tuples 0-1
annot.set_border(width=1, dashes=[3,2], style=None, clouds=0)
annot.set_opacity(0.5)            # 0-1
annot.set_info(title="Author", content="note text", subject="subj", creationDate=None, modDate=None)
annot.set_rect(rect)              # reposition
annot.set_popup(rect)             # popup rectangle
annot.set_name(name)              # icon name for Text/Stamp
annot.set_flags(flags)            # annotation flags
annot.set_rotation(angle)         # rotation in degrees
annot.update(
    fontsize=None, fontname=None, text_color=None, fill_color=None,
    border_color=None, border_width=None, rotate=None,
)
```

#### Delete annotations

```python
page.delete_annot(annot)
```

#### Iterate annotations

```python
for annot in page.annots():
    print(annot.type, annot.info, annot.rect)
```

---

### 1.7 Redaction

```python
annot = page.add_redact_annot(
    quad_or_rect,
    text=None,                     # replacement text overlay
    fontname="helv",
    fontsize=11,
    align=fitz.TEXT_ALIGN_LEFT,
    fill=(1, 1, 1),               # fill color after redaction (RGB)
    text_color=(0, 0, 0),
    cross_out=True,                # show X pattern before applying
)
page.apply_redactions(
    images=fitz.PDF_REDACT_IMAGE_PIXELS,  # PDF_REDACT_IMAGE_NONE, PDF_REDACT_IMAGE_REMOVE, PDF_REDACT_IMAGE_PIXELS
    graphics=fitz.PDF_REDACT_LINE_ART_IF_TOUCHED,  # PDF_REDACT_LINE_ART_NONE, PDF_REDACT_LINE_ART_IF_TOUCHED, PDF_REDACT_LINE_ART_IF_WRAPPED
)
# apply_redactions permanently removes content under redaction areas
```

---

### 1.8 Page Manipulation

```python
# Insert
new_page = doc.new_page(pno=-1, width=595, height=842)  # A4 default; pno=-1 = append
doc.insert_page(pno, text="", fontsize=11, fontname="helv", fontfile=None, color=None, width=595, height=842)

# Delete
doc.delete_page(pno)
doc.delete_pages(from_page=0, to_page=5)
doc.delete_pages([0, 3, 7])       # by list

# Move / Copy
doc.move_page(pno, to=-1)         # move page to position (-1 = end)
doc.copy_page(pno, to=-1)         # copy page to position

# Rotation
page.set_rotation(90)             # 0, 90, 180, 270

# Page boxes
page.set_cropbox(rect)
page.set_mediabox(rect)
page.set_trimbox(rect)
page.set_artbox(rect)
page.set_bleedbox(rect)
# Read
page.rect                         # mediabox as Rect
page.cropbox
page.trimbox
page.artbox
page.bleedbox
```

---

### 1.9 Merge / Split

```python
# Merge pages from another PDF
doc.insert_pdf(
    src_doc,                       # source Document
    from_page=-1,                  # first source page (-1 = first)
    to_page=-1,                    # last source page (-1 = last)
    start_at=-1,                   # insertion point (-1 = end)
    rotate=-1,                     # rotation (-1 = keep)
    links=True,                    # copy links
    annots=True,                   # copy annotations
    show_progress=0,               # print progress every N pages
    final=1,                       # 1 = last insert call (optimizes)
)

# Split: open new empty doc, insert_pdf single page, save (covered by `claw pdf split`)
```

---

### 1.10 Watermarks & Overlays

> Use `claw pdf watermark` / `claw pdf stamp` for the common cases. Three escape-hatch APIs:

- **`page.show_pdf_page(rect, src_doc, pno=0, keep_proportion=True, overlay=True, oc=0, rotation=0, clip=None)`** — overlay any page from any source PDF (best for image stamps).
- **Shape-based** — `page.new_shape()` → `insert_text(point, text, fontsize, color, rotate)` → `finish(color, fill, width, opacity)` → `commit(overlay=True)`.
- **TextWriter** — `fitz.TextWriter(page.rect)` → `append(point, text, fontsize, font)` → `write_text(page, opacity, overlay, color)` — most precise control over fonts and position.

---

### 1.11 Forms (Widgets)

#### Widget types

| Constant | Type |
|----------|------|
| `PDF_WIDGET_TYPE_TEXT` | Text field |
| `PDF_WIDGET_TYPE_CHECKBOX` | Checkbox |
| `PDF_WIDGET_TYPE_COMBOBOX` | Combo box (dropdown) |
| `PDF_WIDGET_TYPE_LISTBOX` | List box |
| `PDF_WIDGET_TYPE_RADIOBUTTON` | Radio button |
| `PDF_WIDGET_TYPE_PUSHBUTTON` | Push button |
| `PDF_WIDGET_TYPE_SIGNATURE` | Signature field |

#### Read widgets

```python
for widget in page.widgets():
    print(widget.field_name, widget.field_type, widget.field_value, widget.rect)
```

#### Fill form fields

```python
for widget in page.widgets():
    if widget.field_name == "Name":
        widget.field_value = "John Doe"
        widget.update()
```

#### Create widget

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
widget.choice_values = ["a", "b"]  # for combobox/listbox
widget.button_caption = "Click"    # for pushbutton
widget.is_signed = False           # for signature
page.add_widget(widget)
```

---

### 1.12 TOC / Bookmarks / Links

#### Table of contents

```python
toc = doc.get_toc(simple=True)     # list of [level, title, page, dest_dict]
# simple=True: [level, title, page]
# simple=False: [level, title, page, {"kind": ..., "to": ..., "page": ...}]

doc.set_toc(toc)                   # set new TOC; same format as get_toc
```

#### Outline (bookmark tree)

```python
outline = doc.outline               # first Outline item or None
while outline:
    print(outline.level, outline.title, outline.page, outline.uri, outline.is_open)
    outline = outline.next
```

#### Links

```python
links = page.get_links()
# each link: {"kind": int, "from": Rect, "uri": str, "page": int, "to": Point, ...}
# kind: LINK_NONE=0, LINK_GOTO=1, LINK_URI=2, LINK_LAUNCH=3, LINK_NAMED=4, LINK_GOTOR=5

page.insert_link({
    "kind": fitz.LINK_URI,
    "from": fitz.Rect(100, 100, 200, 120),
    "uri": "https://example.com",
})
page.insert_link({
    "kind": fitz.LINK_GOTO,
    "from": fitz.Rect(100, 100, 200, 120),
    "page": 5,
    "to": fitz.Point(0, 0),       # destination point on target page
    "zoom": 0,                     # zoom factor (0 = unchanged)
})
page.insert_link({
    "kind": fitz.LINK_GOTOR,
    "from": fitz.Rect(100, 100, 200, 120),
    "file": "other.pdf",
    "page": 0,
    "to": fitz.Point(0, 0),
})
page.insert_link({
    "kind": fitz.LINK_NAMED,
    "from": fitz.Rect(100, 100, 200, 120),
    "name": "FirstPage",          # "FirstPage", "LastPage", "NextPage", "PrevPage"
})
page.insert_link({
    "kind": fitz.LINK_LAUNCH,
    "from": fitz.Rect(100, 100, 200, 120),
    "file": "document.docx",
})

page.delete_link(link_dict)
page.update_link(link_dict)
```

---

### 1.13 Metadata & Encryption

#### Metadata

```python
meta = doc.metadata                # dict with: format, title, author, subject, keywords, creator, producer, creationDate, modDate, trapped, encryption

doc.set_metadata({
    "title": "My Document",
    "author": "Author Name",
    "subject": "Subject",
    "keywords": "key1, key2",
    "creator": "My App",
    "producer": "PyMuPDF",
    "creationDate": "D:20240101000000",
    "modDate": "D:20240101000000",
})

xml = doc.xref_xml_metadata()      # XMP metadata as XML string
```

#### Encryption

```python
doc.authenticate("password")       # unlock encrypted PDF; returns permission flags

doc.save("encrypted.pdf",
    encryption=fitz.PDF_ENCRYPT_AES_256,  # PDF_ENCRYPT_RC4_40, PDF_ENCRYPT_RC4_128, PDF_ENCRYPT_AES_128, PDF_ENCRYPT_AES_256
    owner_pw="owner_pass",
    user_pw="user_pass",
    permissions=
        fitz.PDF_PERM_PRINT |     # allow printing
        fitz.PDF_PERM_MODIFY |    # allow modification
        fitz.PDF_PERM_COPY |      # allow copy
        fitz.PDF_PERM_ANNOTATE |  # allow annotations
        fitz.PDF_PERM_FORM |      # allow form filling
        fitz.PDF_PERM_ACCESSIBILITY | # allow accessibility
        fitz.PDF_PERM_ASSEMBLE |  # allow assembly
        fitz.PDF_PERM_PRINT_HQ,   # allow high-quality printing
)
```

---

### 1.14 Drawing (Shape Class)

```python
shape = page.new_shape()

# Drawing primitives
shape.draw_line(p1, p2)
shape.draw_rect(rect)
shape.draw_circle(center, radius)
shape.draw_oval(rect)
shape.draw_curve(p1, p2, p3)      # quadratic Bezier
shape.draw_bezier(p1, p2, p3, p4) # cubic Bezier
shape.draw_squiggle(p1, p2, breadth=2)
shape.draw_zigzag(p1, p2, breadth=2)
shape.draw_polyline(points)
shape.draw_sector(center, point, angle, fullSector=True)
shape.draw_quad(quad)

# Text
shape.insert_text(point, text, fontsize=11, fontname="helv", fontfile=None, color=(0,0,0), fill=None, render_mode=0, border_width=0.05, rotate=0, morph=None, encoding=fitz.TEXT_ENCODING_LATIN)
rc = shape.insert_textbox(rect, text, fontsize=11, fontname="helv", fontfile=None, color=(0,0,0), fill=None, render_mode=0, border_width=0.05, expandtabs=8, align=fitz.TEXT_ALIGN_LEFT, rotate=0, morph=None, encoding=fitz.TEXT_ENCODING_LATIN)
# rc < 0 means overflow; abs(rc) = unused space

# Finish (apply style to all preceding draws since last finish)
shape.finish(
    color=(0, 0, 0),              # stroke color (RGB 0-1)
    fill=None,                     # fill color
    width=1,                       # line width
    dashes=None,                   # dash pattern string, e.g. "[3 2] 0"
    lineCap=0,                     # 0=butt, 1=round, 2=square
    lineJoin=0,                    # 0=miter, 1=round, 2=bevel
    opacity=1,                     # 0-1
    fill_opacity=1,                # fill opacity separate from stroke
    stroke_opacity=1,              # stroke opacity
    even_odd=False,                # fill rule
    morph=None,                    # (fixpoint, Matrix) morphing
    closePath=True,                # close path
    oc=0,                          # optional content group xref
)

# Commit all finished drawings to page
shape.commit(overlay=True)        # True = foreground, False = background
```

---

### 1.15 TextWriter & Story

#### TextWriter

```python
tw = fitz.TextWriter(page.rect, opacity=1, color=(0,0,0))

tw.append(
    pos,                           # Point: insertion point
    text,                          # string
    font=fitz.Font("helv"),
    fontsize=11,
    language=None,                 # e.g. "en" for text shaping
    right_to_left=False,
    small_caps=False,
)

# Fill a rectangle with text (auto line-wrap)
overflow = tw.fill_textbox(
    rect,
    text,
    pos=None,                      # start position within rect
    font=fitz.Font("helv"),
    fontsize=11,
    align=fitz.TEXT_ALIGN_LEFT,    # TEXT_ALIGN_LEFT, TEXT_ALIGN_CENTER, TEXT_ALIGN_RIGHT, TEXT_ALIGN_JUSTIFY
    warn=True,                     # print overflow warning
    right_to_left=False,
)

tw.write_text(page, overlay=True, morph=None, oc=0, color=None, opacity=None)
# Properties
tw.text_rect                       # bounding rect of written text
tw.last_point                      # last insertion point
```

#### Story (HTML/CSS to PDF)

```python
story = fitz.Story(html="<h1>Title</h1><p>Body text</p>", user_css="h1 {color: red;}")

# DOM manipulation
body = story.body
para = body.add_paragraph()
para.add_span("Hello ", bold=True)
para.add_span("World", italic=True)

# Write to DocumentWriter
writer = fitz.DocumentWriter("output.pdf")
while True:
    device = writer.begin_page(fitz.paper_rect("a4"))
    more, filled = story.place(fitz.Rect(72, 72, 523, 770))  # content rect
    story.draw(device)
    writer.end_page()
    if not more:
        break
writer.close()
```

#### insert_htmlbox

```python
excess = page.insert_htmlbox(
    rect,
    text,                          # HTML string
    css=None,                      # optional CSS
    archive=None,                  # fitz.Archive for images/fonts
    overlay=True,
    rotate=0,
    oc=0,
    opacity=1,
    scale_low=0,                   # min font scale factor (0 = no limit)
)
```

---

### 1.16 Font Handling

```python
font = fitz.Font(
    fontname=None,                 # Base14 name: "helv", "tiro", "cour", "symb", "zadb", "Helvetica", "Times-Roman", "Courier", "Symbol", "ZapfDingbats" + bold/italic variants
    fontfile=None,                 # path to TTF/OTF file
    fontbuffer=None,               # font file bytes
    script=0,                      # script code for CJK
    language=None,
    ordering=-1,                   # CJK: 0=China-S, 1=China-T, 2=Japan, 3=Korea
    is_bold=False,
    is_italic=False,
    is_serif=True,
)

# Properties
font.name                          # font name
font.flags                         # font flags dict
font.is_bold, font.is_italic
font.is_writable                   # can use for text insertion
font.ascender, font.descender
font.glyph_count
font.text_length(text, fontsize=11)  # rendered text width
font.char_lengths(text, fontsize=11) # list of char widths
font.glyph_bbox(chr)              # glyph bounding box
font.has_glyph(chr)               # check glyph existence
font.valid_codepoints()           # list of supported codepoints
font.buffer                       # font file bytes (for subsetting)
```

---

### 1.17 Optional Content (Layers / OCG)

```python
# Create Optional Content Group
xref = doc.add_ocg(name, config=-1, on=True, intent="View", usage="Artwork")

# Create Optional Content Membership Dict
xref = doc.set_ocmd(
    ocgs=None,                     # list of OCG xrefs
    policy="AnyOn",                # "AnyOn", "AnyOff", "AllOn", "AllOff"
    ve=None,                       # visibility expression
)

# Assign OC to content
page.insert_text(point, "Layer text", fontsize=12, oc=ocg_xref)
page.insert_image(rect, filename="image.png", oc=ocg_xref)
page.show_pdf_page(rect, src, pno=0, oc=ocg_xref)
shape.finish(oc=ocg_xref)
# oc parameter available on most content-insertion methods

# Toggle visibility
doc.set_layer_ui_config(number, action=0)  # 0=toggle, 1=on, 2=off
# Get layer info
layers = doc.layer_ui_configs()
# Get/set default configuration
doc.get_layer(-1)
```

---

### 1.18 OCR (Tesseract Integration)

```python
tp = page.get_textpage_ocr(
    flags=0,
    language="eng",                # Tesseract language code(s), e.g. "eng+deu"
    dpi=72,                        # resolution for OCR
    full=False,                    # True = OCR entire page; False = only non-text areas
    tessdata=None,                 # path to tessdata directory
)
text = page.get_text("text", textpage=tp)
```

---

## 2. PyPDF2 -- PDF Merge / Split / Transform

```python
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
```

> This skill standardises on `PyPDF2` (installed by default — see `setup.md` and `scripts/healthcheck.py`). The maintained fork `pypdf` exposes a near-identical API; to switch, `pip install pypdf` and replace `PyPDF2` with `pypdf` in the imports below.

### 2.1 Core Operations

#### Read

```python
reader = PdfReader("input.pdf")
reader = PdfReader(file_stream)
reader = PdfReader("encrypted.pdf", password="secret")

reader.pages                       # list-like of PageObject
len(reader.pages)                  # page count
page = reader.pages[0]
```

#### Write

```python
writer = PdfWriter()
writer.add_page(page)              # append page
writer.insert_page(page, index=0)  # insert at position
writer.add_blank_page(width=612, height=792)

writer.write("output.pdf")
writer.write(file_stream)

# Clone reader into writer for modification
writer = PdfWriter(clone_from="input.pdf")
writer = PdfWriter(clone_from=reader)
```

#### Merge

```python
merger = PdfMerger()
merger.append("file1.pdf")
merger.append("file2.pdf", pages=(0, 5))       # page range (start, end)
merger.append("file3.pdf", pages=(0, 10, 2))   # (start, end, step)
merger.merge(position=2, "insert.pdf")          # insert at page index
merger.write("merged.pdf")
merger.close()
```

---

### 2.2 Page Transforms

```python
page.rotate(90)                    # clockwise rotation: 90, 180, 270
page.scale(sx, sy)                 # scale factors
page.scale_to(width, height)       # scale to exact dimensions
page.merge_page(overlay_page)      # overlay another page (watermark/stamp)
page.merge_transformed_page(page2, transformation)  # with Transformation object

# Transformation object
from PyPDF2 import Transformation
op = Transformation().rotate(45).scale(1.5).translate(tx=100, ty=50)
page.add_transformation(op)

# Page boxes
page.mediabox                      # RectangleObject
page.cropbox
page.trimbox
page.bleedbox
page.artbox
# Settable:
page.cropbox = PyPDF2.generic.RectangleObject([0, 0, 300, 400])
```

---

### 2.3 Text & Image Extraction

#### Text

```python
text = page.extract_text()
text = page.extract_text(
    visitor_body=None,             # callable(text, cm, tm, fontDict, fontSize)
    visitor_text=None,             # callable(text, cm, tm, fontDict, fontSize)
    visitor_operand_before=None,   # callable(operand, operands, cm, tm)
)

# Layout mode (preserves spatial layout)
text = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=True, layout_mode_scale_weight=1.25, layout_mode_strip_rotated=True)
```

#### Images

```python
for image in page.images:
    print(image.name, image.data)  # name and bytes
    with open(image.name, "wb") as f:
        f.write(image.data)

# Alternative: low-level
if "/XObject" in page["/Resources"]:
    for obj_name in page["/Resources"]["/XObject"]:
        xobj = page["/Resources"]["/XObject"][obj_name]
        if xobj["/Subtype"] == "/Image":
            # extract image data
            pass
```

---

### 2.4 Metadata & Security

#### Metadata

```python
meta = reader.metadata             # DocumentInformation object
meta.title, meta.author, meta.subject, meta.creator, meta.producer

# XMP metadata
xmp = reader.xmp_metadata

# Write metadata
writer.add_metadata({
    "/Title": "My Doc",
    "/Author": "Author",
    "/Subject": "Subject",
    "/Keywords": "key1, key2",
    "/Creator": "My App",
    "/Producer": "PyPDF2",
})
```

#### Encryption / Decryption

```python
# Decrypt
reader = PdfReader("encrypted.pdf")
reader.decrypt("password")

# Encrypt
writer.encrypt(
    user_password="user",
    owner_password="owner",        # None = same as user
    use_128bit=True,               # False = RC4-40, True = RC4-128
    permissions_flag=-1,           # -1 = all permissions
    algorithm=None,                # "RC4-40", "RC4-128", "AES-128", "AES-256", "AES-256-R5"
)
```

---

### 2.5 Bookmarks & Annotations

#### Outlines (bookmarks)

```python
# Read
outlines = reader.outline          # nested list of Destination objects

# Add
writer.add_outline_item(
    title="Chapter 1",
    page_number=0,                 # 0-based
    parent=None,                   # parent outline item for nesting
    before=None,                   # insert before this item
    color=None,                    # (R, G, B) tuple 0-1
    bold=False,
    italic=False,
    fit="/Fit",                    # /Fit, /FitH, /FitV, /FitB, /FitBH, /FitBV, /XYZ, /FitR
    is_open=True,                  # expanded by default
)
```

#### Annotations

```python
from PyPDF2.annotations import (
    Text, FreeText, Line, PolyLine, Polygon, Rectangle, Circle,
    Highlight, Underline, Squiggly, StrikeOut, Stamp, Ink, Link,
)
# Each takes rect + class-specific kwargs. Examples:
#   Highlight(rect=(x1,y1,x2,y2), quad_points=None)
#   FreeText(rect=..., text=..., font="Helvetica", font_size="12pt", font_color="000000",
#            border_color="000000", background_color="ffffff")
#   Stamp(rect=..., name="Approved")
#   Ink(paths=[[(x1,y1),(x2,y2)]], color="ff0000")
#   Link(rect=..., url="https://example.com")   # external
#   Link(rect=..., target_page_index=3)          # internal
writer.add_annotation(page_number=0, annotation=annot)
```

---

### 2.6 Forms & Attachments

#### Forms

```python
# Read
fields = reader.get_fields()       # dict of field_name: field_info
text_fields = reader.get_form_text_fields()  # dict of name: value

# Fill
writer.update_page_form_field_values(
    page=writer.pages[0],
    fields={"field_name": "value", "checkbox1": "/Yes"},
    auto_regenerate=True,
)

# Flatten (make fields non-editable)
# write filled PDF, then render each page as image and re-insert, or use:
for page in writer.pages:
    for annot in page.get("/Annots", []):
        annot_obj = annot.get_object()
        if annot_obj.get("/Subtype") == "/Widget":
            annot_obj[PyPDF2.generic.NameObject("/Ff")] = PyPDF2.generic.NumberObject(1)  # read-only
```

#### Attachments

```python
# Add
writer.add_attachment(filename="data.csv", data=b"col1,col2\na,b")

# Read embedded files
catalog = reader.trailer["/Root"]
if "/Names" in catalog and "/EmbeddedFiles" in catalog["/Names"]:
    # traverse name tree
    pass
```

---

### 2.7 Viewer Preferences

```python
writer.page_layout = "/SinglePage"   # /SinglePage, /OneColumn, /TwoColumnLeft, /TwoColumnRight, /TwoPageLeft, /TwoPageRight
writer.page_mode = "/UseOutlines"    # /UseNone, /UseOutlines, /UseThumbs, /FullScreen, /UseOC, /UseAttachments

writer.viewer_preferences = {
    "/HideToolbar": True,
    "/HideMenubar": True,
    "/HideWindowUI": False,
    "/FitWindow": True,
    "/CenterWindow": True,
    "/DisplayDocTitle": True,
    "/NonFullScreenPageMode": "/UseNone",
    "/Direction": "/L2R",
    "/PrintScaling": "/None",
    "/Duplex": "/Simplex",
    "/PrintPageRange": [0, 4],
    "/NumCopies": 1,
}
```

---

## 3. pdfplumber -- PDF Data Extraction

```python
import pdfplumber
```

### 3.1 Open & Page Properties

```python
pdf = pdfplumber.open("file.pdf")
pdf = pdfplumber.open("file.pdf", password="secret")
pdf = pdfplumber.open(file_stream)

pdf.pages                          # list of Page objects
pdf.metadata                       # dict
page = pdf.pages[0]

# Page properties
page.page_number                   # 1-based
page.width, page.height
page.bbox                          # (x0, top, x1, bottom)
page.mediabox, page.cropbox, page.trimbox, page.artbox, page.bleedbox
```

### 3.2 Page Objects

Access underlying PDF objects as lists of dicts:

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

---

### 3.3 Text Extraction

#### extract_text

```python
text = page.extract_text(
    x_tolerance=3,                 # max horizontal gap to merge chars
    x_tolerance_ratio=None,        # ratio of font size (overrides x_tolerance)
    y_tolerance=3,                 # max vertical gap to merge lines
    layout=False,                  # True = spatial layout mode
    layout_width=0,                # override page width for layout
    layout_height=0,               # override page height for layout
    layout_width_chars=0,          # character-based width
    layout_height_chars=0,
    x_shift=0,                     # horizontal offset
    y_shift=0,                     # vertical offset
    x_density=7.25,                # chars per point (layout)
    y_density=13.0,                # lines per point (layout)
    use_text_flow=False,           # follow PDF content stream order
    keep_blank_chars=False,        # keep zero-width blanks
    extra_attrs=None,              # group chars by additional attributes
    split_at_punctuation=False,    # True or string of punctuation chars
)
```

#### extract_text_simple

```python
text = page.extract_text_simple(x_tolerance=3, y_tolerance=3)
```

#### extract_words

```python
words = page.extract_words(
    x_tolerance=3,
    y_tolerance=3,
    keep_blank_chars=False,
    use_text_flow=False,
    extra_attrs=None,              # list of char attributes to include, e.g. ["fontname", "size"]
    split_at_punctuation=False,    # True or str of chars
    expand_ligatures=True,
    return_chars=False,            # include constituent chars
)
# each word: {"text", "x0", "top", "x1", "bottom", "upright", "direction", "fontname"*, "size"*, ...}
```

#### extract_text_lines

```python
lines = page.extract_text_lines(
    layout=False,
    strip=True,
    return_chars=True,
    x_tolerance=3, y_tolerance=3,
)
# each line: {"text", "x0", "top", "x1", "bottom", "chars": [...]}
```

#### search

```python
results = page.search(
    pattern,                       # string or compiled regex
    regex=True,                    # treat as regex
    case=True,                     # case-sensitive
    x_tolerance=3,
    y_tolerance=3,
    return_chars=True,
    return_groups=True,
    layout=False,
)
# each result: {"text", "x0", "top", "x1", "bottom", "chars": [...], "groups": [...]}
```

---

### 3.4 Table Extraction

```python
# Find tables (returns TableFinder)
tables = page.find_tables(
    table_settings={
        "vertical_strategy": "lines",      # "lines", "lines_strict", "text", "explicit"
        "horizontal_strategy": "lines",    # same options
        "explicit_vertical_lines": [],     # list of x-coordinates or line dicts
        "explicit_horizontal_lines": [],   # list of y-coordinates or line dicts
        "snap_tolerance": 3,               # snap nearby lines together
        "snap_x_tolerance": 3,
        "snap_y_tolerance": 3,
        "join_tolerance": 3,               # join nearby line segments
        "join_x_tolerance": 3,
        "join_y_tolerance": 3,
        "edge_min_length": 3,              # minimum edge length to consider
        "min_words_vertical": 3,           # min words to infer vertical boundary (text strategy)
        "min_words_horizontal": 1,         # min words to infer horizontal boundary
        "intersection_tolerance": 3,       # tolerance for line intersection detection
        "intersection_x_tolerance": 3,
        "intersection_y_tolerance": 3,
        "text_tolerance": 3,               # tolerance for text-based strategy
        "text_x_tolerance": 3,
        "text_y_tolerance": 3,
    }
)
# tables -> list of Table objects
# tables[0].bbox -> (x0, top, x1, bottom)
# tables[0].cells -> list of cell bboxes
# tables[0].rows -> list of Row objects

# Extract data
data = tables[0].extract()         # list of lists (rows x cols); None for empty cells

# Single table shortcuts
table = page.find_table()          # first table
data = page.extract_table()        # extract first table data
all_data = page.extract_tables()   # extract all tables data

# Debug
page.debug_tablefinder(table_settings={})  # returns PageImage with table detection overlay
```

**Strategy guide:**

| Strategy | Use when |
|----------|----------|
| `"lines"` | Table has visible ruling lines (default) |
| `"lines_strict"` | Only use lines that form complete intersections |
| `"text"` | Infer boundaries from text alignment |
| `"explicit"` | Provide exact line positions manually |

---

### 3.5 Visual Debugging

```python
im = page.to_image(resolution=150, antialias=True)

# Draw on image
im.draw_line(points_or_obj, stroke="red", stroke_width=1)
im.draw_lines(list_of_lines, stroke="red", stroke_width=1)
im.draw_vline(x, stroke="blue", stroke_width=1)
im.draw_hline(y, stroke="blue", stroke_width=1)
im.draw_vlines(xs, stroke="blue", stroke_width=1)
im.draw_hlines(ys, stroke="blue", stroke_width=1)
im.draw_rect(bbox_or_obj, fill=None, stroke="green", stroke_width=1)
im.draw_rects(list_of_rects, fill=None, stroke="green", stroke_width=1)
im.draw_circle(center_or_obj, radius=5, fill=None, stroke="green", stroke_width=1)
im.draw_circles(list_of_circles, radius=5, fill=None, stroke="green", stroke_width=1)

# Table debugging overlay
im.debug_tablefinder(table_settings={})

# Save / display
im.save("debug.png", format="PNG", quantize=True, colors=256, bits=8)
im.show()                          # open in default viewer
im.reset()                         # clear drawings
```

---

### 3.6 Crop & Filter

```python
# Crop to bounding box (x0, top, x1, bottom)
cropped = page.crop((0, 0, page.width/2, page.height))  # left half
cropped.extract_text()             # extract from cropped region

# within_bbox: keep only objects fully inside bbox
filtered = page.within_bbox((x0, top, x1, bottom))

# outside_bbox: keep only objects fully outside bbox
filtered = page.outside_bbox((x0, top, x1, bottom))

# filter: custom predicate
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

### 4.1 Canvas Drawing

```python
from reportlab.pdfgen import canvas

c = canvas.Canvas("output.pdf", pagesize=letter)
# pagesize = (width, height) in points; 1 inch = 72 points
```

#### Lines & Shapes

```python
c.line(x1, y1, x2, y2)
c.lines([(x1,y1,x2,y2), ...])     # multiple lines
c.rect(x, y, width, height, stroke=1, fill=0)
c.roundRect(x, y, width, height, radius, stroke=1, fill=0)
c.circle(x_center, y_center, radius, stroke=1, fill=0)
c.ellipse(x1, y1, x2, y2, stroke=1, fill=0)
c.wedge(x1, y1, x2, y2, startAng, extent, stroke=1, fill=0)
c.arc(x1, y1, x2, y2, startAng, extent)
c.bezier(x1, y1, x2, y2, x3, y3, x4, y4)
c.grid(xlist, ylist)               # draw grid from coordinate lists

# Path object
p = c.beginPath()
p.moveTo(x, y)
p.lineTo(x, y)
p.curveTo(x1, y1, x2, y2, x3, y3)  # cubic Bezier
p.arcTo(x1, y1, x2, y2, startAng, extent)
p.rect(x, y, w, h)
p.ellipse(x, y, w, h)
p.circle(x, y, r)
p.close()
c.drawPath(p, stroke=1, fill=0)
c.clipPath(p, stroke=0, fill=0)    # set clipping region
```

#### Text

```python
c.drawString(x, y, text)           # left-aligned at (x, y) baseline
c.drawRightString(x, y, text)      # right-aligned
c.drawCentredString(x, y, text)    # centered
c.drawAlignedString(x, y, text, pivotChar=".")  # decimal-aligned

# Text object (advanced control)
t = c.beginText(x, y)
t.setFont("Helvetica", 12)
t.setCharSpace(0)                  # extra space between chars
t.setWordSpace(0)                  # extra space between words
t.setLeading(14.4)                 # line spacing
t.setRise(0)                       # superscript/subscript offset
t.setHorizScale(100)               # horizontal scaling %
t.setRenderingMode(0)              # 0=fill, 1=stroke, 2=fill+stroke, 3=invisible, 4-7=clipping variants
t.textLine("First line")           # write line and advance
t.textLines("Line1\nLine2\nLine3") # multi-line
t.moveCursor(dx, dy)               # relative move
t.setTextOrigin(x, y)             # absolute move
c.drawText(t)
```

#### Images

```python
c.drawImage(
    image,                         # filename, path, or ImageReader object
    x, y,
    width=None, height=None,       # None = natural size
    mask=None,                     # "auto" for transparency, or [r1,r2,g1,g2,b1,b2] color range
    preserveAspectRatio=False,
    showBoundary=False,
    anchor="sw",                   # anchor point: c, n, ne, e, se, s, sw, w, nw
)
c.drawInlineImage(image, x, y, width=None, height=None)  # embed image inline (no compression)
# Supported: JPEG, PNG, GIF, BMP, TIFF, PIL Image objects
```

#### Colors & Opacity

```python
c.setStrokeColor(colors.red)       # named color (140+ colors available)
c.setFillColor(colors.blue)
c.setStrokeColorRGB(r, g, b)      # 0-1 floats
c.setFillColorRGB(r, g, b)
c.setStrokeColorCMYK(c, m, y, k)
c.setFillColorCMYK(c, m, y, k)
c.setStrokeGray(level)             # 0=black, 1=white
c.setFillGray(level)
c.setFillColor(HexColor("#FF5733"))
c.setFillAlpha(0.5)                # fill opacity 0-1
c.setStrokeAlpha(0.5)              # stroke opacity 0-1
c.setFillOverprint(False)
c.setStrokeOverprint(False)
```

#### State & Transforms

```python
c.saveState()                      # push graphics state
c.restoreState()                   # pop graphics state

c.translate(tx, ty)
c.scale(sx, sy)
c.rotate(degrees)                  # counter-clockwise
c.skew(alpha, beta)                # x-skew, y-skew in degrees
c.transform(a, b, c, d, e, f)     # full affine matrix [a b 0; c d 0; e f 1]
```

#### Line Style

```python
c.setLineWidth(width)
c.setLineCap(0)                    # 0=butt, 1=round, 2=projecting square
c.setLineJoin(0)                   # 0=miter, 1=round, 2=bevel
c.setDash(array=[], phase=0)       # e.g. setDash([6,3], 0) or setDash(6, 3)
c.setMiterLimit(10)
```

#### Page Control

```python
c.showPage()                       # finalize current page, start new
c.save()                           # finalize and write PDF

c.setPageSize(A4)
c.setPageRotation(90)
```

---

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

#### Document Templates

```python
# Simple (single frame per page)
doc = SimpleDocTemplate(
    "output.pdf",
    pagesize=letter,
    topMargin=72, bottomMargin=72, leftMargin=72, rightMargin=72,
    title="Title", author="Author", subject="Subject", creator="Creator",
    showBoundary=0,                # debug: show frame boundaries
)
doc.build(flowables_list, onFirstPage=header_func, onLaterPages=header_func)

# Advanced (custom templates)
doc = BaseDocTemplate("output.pdf", pagesize=letter)
frame1 = Frame(x1, y1, width, height, id="col1", leftPadding=6, rightPadding=6, topPadding=6, bottomPadding=6, showBoundary=0)
frame2 = Frame(x2, y2, width, height, id="col2")
template = PageTemplate(id="TwoColumn", frames=[frame1, frame2], onPage=draw_header_footer)
doc.addPageTemplates([template])
doc.build(flowables_list)

# onPage / onPageEnd callback signature:
def draw_header_footer(canvas, doc):
    canvas.saveState()
    canvas.drawString(72, 750, f"Page {doc.page}")
    canvas.restoreState()
```

#### Flowables

**Paragraph** (rich text with inline markup):

```python
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

styles = getSampleStyleSheet()
# Built-in styles: Normal, BodyText, Title, Heading1-6, Italic, Code, Bullet, Definition, OrderedList, UnorderedList

p = Paragraph("Text with <b>bold</b>, <i>italic</i>, <u>underline</u>", styles["Normal"])
```

Supported inline tags:
- `<b>`, `<i>`, `<u>`, `<strike>`
- `<a href="url">link</a>`, `<a name="anchor">`
- `<font name="Courier" size="14" color="red">styled</font>`
- `<br/>` line break
- `<sub>`, `<super>` (subscript/superscript)
- `<img src="file.png" width="50" height="50" valign="middle"/>`
- `<bullet>` for bullet prefix
- `<seq id="name"/>` auto-numbering
- `<greek>`, `<unichar code="0xNNNN"/>`
- `<span>` with style attributes

**ParagraphStyle** — full kwarg list (extends `parent=styles["Normal"]`):

`name`, `parent`, `fontName`, `fontSize`, `leading` (line height), `alignment` (TA_LEFT/CENTER/RIGHT/JUSTIFY), `leftIndent`, `rightIndent`, `firstLineIndent`, `spaceBefore`, `spaceAfter`, `textColor`, `backColor`, `borderWidth`, `borderColor`, `borderPadding`, `borderRadius`, `wordWrap` (`"CJK"` for CJK), `bulletFontName`, `bulletFontSize`, `bulletIndent`, `bulletColor`, `bulletAnchor`, `bulletText`, `endDots` (TOC dot leader), `splitLongWords`, `underlineWidth`, `strikeWidth`, `underlineColor`, `strikeColor`, `underlineOffset`, `strikeOffset`, `textTransform` (`"uppercase"`/`"lowercase"`/`"capitalize"`), `allowWidows`, `allowOrphans`.

**Table** kwargs: `data` (2D list), `colWidths` (list or `None`=auto), `rowHeights`, `style`, `splitByRow=1` (row-wise page split), `splitInRow=0` (split inside a row), `repeatRows=0` (header rows repeated per page), `repeatCols=0`, `hAlign` (LEFT/CENTER/RIGHT), `vAlign` (TOP/MIDDLE/BOTTOM), `cellStyles`, `cornerRadii=[tl,tr,bl,br]`.

**TableStyle commands** — cell refs `(col, row)` 0-based, `-1` = last:

| Category | Commands |
|---|---|
| Color | `BACKGROUND`, `TEXTCOLOR`, `ROWBACKGROUNDS` (alternating list), `COLBACKGROUNDS` |
| Alignment | `ALIGN` (LEFT/CENTER/RIGHT/DECIMAL), `VALIGN` (TOP/MIDDLE/BOTTOM) |
| Font | `FONT`, `FONTNAME`, `FONTSIZE`, `LEADING` |
| Borders | `GRID`, `BOX`, `LINEBELOW`, `LINEABOVE`, `LINEBEFORE`, `LINEAFTER` |
| Padding | `TOPPADDING`, `BOTTOMPADDING`, `LEFTPADDING`, `RIGHTPADDING` |
| Layout | `SPAN` (merge cells), `NOSPLIT` (no row split), `ROUNDEDCORNERS [tl,tr,bl,br]` |

Usage: `TableStyle([(cmd, (c0,r0), (c1,r1), *args), ...])` then `table.setStyle(style)`.

**Other Flowables:**

```python
Image(filename, width=None, height=None, kind="direct", mask="auto", lazy=1, hAlign="CENTER")
# kind: "direct" (points), "percentage", "inch", "cm", "mm"

Spacer(width, height)
PageBreak()
FrameBreak()                       # move to next frame
CondPageBreak(height)              # page break if less than height remaining
KeepTogether(flowables_list)       # keep group on same page
KeepInFrame(maxWidth, maxHeight, content=[], mode="shrink", mergeSpace=1, hAlign="CENTER", vAlign="MIDDLE", fakeWidth=None)
# mode: "error", "overflow", "shrink", "truncate"

Preformatted(text, style, dedent=0, maxLineLength=None, splitChars=None, newLineChars=None)
XPreformatted(text, style)         # like Preformatted but supports XML tags

ListFlowable(
    items,                         # list of ListItem or Flowable or string
    bulletType="bullet",           # "bullet", "1", "a", "A", "i", "I"
    start=None,                    # starting number/letter
    bulletFontName="Helvetica",
    bulletFontSize=12,
    bulletDedent=36,
    bulletDir="ltr",
    bulletFormat=None,             # e.g. "%s." to add period
    bulletOffsetY=0,
)

BalancedColumns(
    F,                             # list of flowables
    nCols=2,
    needed=72,
    spaceBefore=0, spaceAfter=0,
    showBoundary=None,
    leftPadding=None, rightPadding=None,
    topPadding=None, bottomPadding=None,
    innerPadding=None,
    name="",
    endSlack=0.1,
)

# TOC
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle(name="TOC1", fontName="Helvetica-Bold", fontSize=14, leading=16, leftIndent=20, firstLineIndent=-20, spaceBefore=5, spaceAfter=0),
    ParagraphStyle(name="TOC2", fontName="Helvetica", fontSize=12, leading=14, leftIndent=40, firstLineIndent=-20),
]
# Register TOC entries via doc.notify("TOCEntry", (level, text, pageNum, key))

# Index
index = SimpleIndex(dot=" . ", headers=True)
```

**NextPageTemplate:**

```python
# Switch page template
flowables = [
    NextPageTemplate("TwoColumn"),
    PageBreak(),
    Paragraph("Now in two columns", style),
]
```

---

### 4.3 Fonts

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# Base14 fonts (always available):
# Helvetica, Helvetica-Bold, Helvetica-Oblique, Helvetica-BoldOblique
# Times-Roman, Times-Bold, Times-Italic, Times-BoldItalic
# Courier, Courier-Bold, Courier-Oblique, Courier-BoldOblique
# Symbol, ZapfDingbats

# Register TrueType / OpenType
pdfmetrics.registerFont(TTFont("MyFont", "/path/to/font.ttf"))
pdfmetrics.registerFont(TTFont("MyFont-Bold", "/path/to/font-bold.ttf"))
pdfmetrics.registerFont(TTFont("MyFont-Italic", "/path/to/font-italic.ttf"))
pdfmetrics.registerFont(TTFont("MyFont-BoldItalic", "/path/to/font-bi.ttf"))

# Register font family (for <b> <i> in Paragraphs)
pdfmetrics.registerFontFamily(
    "MyFont",
    normal="MyFont",
    bold="MyFont-Bold",
    italic="MyFont-Italic",
    boldItalic="MyFont-BoldItalic",
)

# CJK fonts
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))     # Simplified Chinese
pdfmetrics.registerFont(UnicodeCIDFont("MSung-Light"))      # Traditional Chinese
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))     # Japanese
pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))  # Korean

# Font metrics
face = pdfmetrics.getFont("Helvetica").face
face.ascent, face.descent
pdfmetrics.stringWidth("text", "Helvetica", 12)  # width in points

# Subsetting (automatic for TTF when using Canvas/PLATYPUS)
# Set to False to embed full font:
TTFont("MyFont", "font.ttf", subfontIndex=0)  # for TTC collections
```

---

### 4.4 Charts (reportlab.graphics)

```python
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.spider import SpiderChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF, renderSVG
```

Chart classes share the same shape — set `x`/`y`/`width`/`height`, assign `.data` (list of series lists), configure axes via `chart.valueAxis` / `chart.categoryAxis`, then `drawing.add(chart)`.

- **VerticalBarChart / HorizontalBarChart** — `.data` grouped series, `.bars[i].fillColor`, `.barWidth`, `.groupSpacing`, `.barSpacing`. Stacked via `chart.style = "stacked"`. Axis config: `valueAxis.valueMin/Max/Step`, `categoryAxis.labels.{boxAnchor,dx,dy,angle}`, `categoryAxis.categoryNames`.
- **HorizontalLineChart** — `.lines[i].{strokeColor,strokeWidth,symbol}`, `.joinedLines = 1`. Use `makeMarker("Circle")` for symbols.
- **Pie / Pie3d** — `.data`, `.labels`, `.slices[i].{popout,fillColor}`, `.sideLabels`, `.simpleLabels`, `Pie3d.perspective`.
- **SpiderChart** — `.data`, `.labels`, `.strands[i].{fillColor,strokeColor}` (use `Color(r,g,b,a)` for RGBA).
- **Legend** — `.x`, `.y`, `.alignment`, `.colorNamePairs`, `.columnMaximum`, `.fontName`, `.fontSize`. Add with `drawing.add(legend)`.

#### Render to various formats

```python
renderPDF.drawToFile(drawing, "chart.pdf", "Title")
renderPDF.draw(drawing, canvas, x, y)  # draw onto existing canvas
renderSVG.drawToFile(drawing, "chart.svg")

# To bitmap (requires rlextra or Pillow):
from reportlab.graphics import renderPM
renderPM.drawToFile(drawing, "chart.png", fmt="PNG", dpi=150)
```

---

### 4.5 Barcodes

```python
from reportlab.graphics.barcode import code39, code93, code128, eanbc, usps, fourstate
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
```

#### 1D Barcodes

```python
# On canvas directly
from reportlab.graphics.barcode import createBarcodeDrawing

bc = createBarcodeDrawing(
    "Code128",                     # barcode type
    value="ABC123",
    barWidth=0.01*inch,
    barHeight=0.5*inch,
    humanReadable=True,
)
bc.drawOn(c, x, y)

# Available types:
# "Code39", "Extended39"
# "Code93", "Extended93"
# "Code128", "Code128Auto"
# "EAN8", "EAN13", "UPCA", "UPCE"
# "I2of5"  (Interleaved 2 of 5)
# "ITF"
# "MSI"
# "Codabar"
# "POSTNET"
# "USPS_4State" / "FIM"
# "Standard39", "Standard93"

# Individual barcode classes
bc = code128.Code128("ABC123", barWidth=0.36*mm, barHeight=10*mm, humanReadable=True, quiet=True)
bc = code39.Standard39("ABC", barWidth=0.36*mm, barHeight=10*mm, humanReadable=True, checksum=0)
bc = eanbc.Ean13BarcodeWidget("5901234123457")
bc = eanbc.Ean8BarcodeWidget("55123457")
```

#### 2D Barcodes (QR Code)

```python
qr = QrCodeWidget(
    value="https://example.com",
    barLevel="M",                  # L=7%, M=15%, Q=25%, H=30% error correction
    barWidth=2*inch,
    barHeight=2*inch,
    barBorder=4,                   # quiet zone modules
    barFillColor=colors.black,
    barStrokeColor=colors.black,
    barStrokeWidth=0,
)
d = Drawing(200, 200)
d.add(qr)
d.drawOn(c, x, y)

# Or use createBarcodeDrawing
qr_drawing = createBarcodeDrawing("QR", value="data", barLevel="H", barBorder=4, width=150, height=150)
```

---

### 4.6 Other Features

#### TOC & Index (canvas level)

```python
c.bookmarkPage("key")              # set bookmark at current page
c.addOutlineEntry("Title", "key", level=0, closed=None)  # add to outline/bookmarks
c.bookmarkHorizontalAbsolute("key", top)  # bookmark at specific y position

# Internal links
c.linkRect("text", "key", (x1,y1,x2,y2), relative=1, thickness=0, color=colors.blue)
c.linkAbsolute("text", "key", (x1,y1,x2,y2))
c.linkURL("https://example.com", (x1,y1,x2,y2), relative=0, thickness=0)
```

#### Page Numbers (PLATYPUS)

```python
from reportlab.platypus import PageBreak
from reportlab.lib.sequencer import getSequencer

# Via onPage callback:
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawString(inch, 0.5*inch, f"Page {doc.page}")
    canvas.drawRightString(7.5*inch, 0.5*inch, f"{doc.page}")
    canvas.restoreState()

# Via Paragraph with special tags:
Paragraph("Page <seq id='page'/>", style)
# Or use PageNumberPlaceholder:
# canvas.drawString(x, y, "Page %d" % canvas.getPageNumber())
```

#### Multi-Column Layouts

```python
# Via BaseDocTemplate with multiple Frames per PageTemplate (see 4.2)
# Or BalancedColumns flowable (see 4.2)
```

#### Encryption

```python
from reportlab.lib.pdfencrypt import StandardEncryption

enc = StandardEncryption(
    userPassword="user",
    ownerPassword="owner",
    strength=256,                  # 40, 128, or 256
    canPrint=1, canModify=0, canCopy=0, canAnnotate=0,
    canFillForms=0, canExtract=0, canAssemble=0, canPrintHighRes=0,
)
c = canvas.Canvas("encrypted.pdf", encrypt=enc)
# or
doc = SimpleDocTemplate("encrypted.pdf", encrypt=enc)
```

#### AcroForms (Interactive Forms)

All `c.acroForm.*()` calls share common kwargs: `name`, `tooltip`, `x`, `y`, `width`, `height` (or `size` for buttons), `fontName`, `fontSize`, `borderColor`, `fillColor`, `textColor`, `forceBorder`.

| Call | Extra kwargs |
|---|---|
| `textfield` | `value`, `maxlen`, `fieldFlags` ∈ {`readOnly`, `required`, `noExport`, `multiline`, `password`, `fileSelect`, `doNotSpellCheck`, `doNotScroll`, `comb`, `richText`} |
| `checkbox` | `buttonStyle` ∈ {`check`, `circle`, `cross`, `diamond`, `square`, `star`}, `checked` |
| `radio` | `value` (unique per group), `selected`, `buttonStyle` |
| `choice` | `options=[(val, label), ...]`, `value`, `fieldFlags` ∈ {`combo`, `""` (listbox), `combo\|edit`} |
| `listbox` | `options`, `value` (list), `fieldFlags="multiSelect"` |

#### SVG Support

```python
from reportlab.graphics import renderSVG
from svglib.svglib import svg2rlg

drawing = svg2rlg("input.svg")     # returns Drawing object
drawing.width = 400                # resize
drawing.height = 300
drawing.scale(0.5, 0.5)

renderPDF.drawToFile(drawing, "from_svg.pdf")
# or draw onto canvas:
renderPDF.draw(drawing, canvas, x, y)
# or add to PLATYPUS as flowable
```

---

## Quick Selection Guide

| Task | Best Library |
|------|-------------|
| Generate PDF from scratch | reportlab |
| Read/extract text | PyMuPDF (fitz) or pdfplumber |
| Extract tables | pdfplumber (most configurable) or PyMuPDF |
| Merge/split PDFs | PyMuPDF or pypdf |
| Add annotations | PyMuPDF (most complete) |
| Fill form fields | PyMuPDF or pypdf |
| Render pages to images | PyMuPDF (fitz) |
| Redact content | PyMuPDF |
| Encrypt/decrypt | PyMuPDF or pypdf |
| OCR scanned PDFs | PyMuPDF + Tesseract |
| Visual debugging of extraction | pdfplumber |
| HTML/CSS to PDF | PyMuPDF Story or reportlab PLATYPUS |
| Charts in PDF | reportlab.graphics |
| Barcodes / QR codes | reportlab.graphics.barcode |
| Watermarks/overlays | PyMuPDF or pypdf |

---

## Escape-hatch recipes

Things `claw pdf` doesn't wrap and that genuinely need the library APIs above.

### 1. Custom reportlab `Canvas` layout with per-page header/footer callback

PLATYPUS documents with a branded header/footer require a `PageTemplate` callback — `claw pdf from-md` won't express this shape:

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

A "review stack" with popups and reply threads — not wrappable via flags:

```python
import fitz
doc = fitz.open("manuscript.pdf")
page = doc[0]
parent = page.add_text_annot((72, 72), "Tighten wording?", icon="Comment")
parent.set_info(title="Reviewer A")
parent.update()
# Reply (IRT) — point back via /IRT reference in the XML
reply = page.add_text_annot((72, 90), "Agreed — will redraft.", icon="Comment")
reply.set_info(title="Reviewer B")
reply._irt_xref = parent.xref       # /IRT = In Reply To
reply.update()
doc.saveIncr()
```

### 4. AcroForm-signed fill + flatten with `reportlab` + `pypdf`

Fill in reportlab (adds fields), sign externally, flatten via pypdf — a pipeline claw won't reconstruct.

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

The escape hatch for "I want HTML+CSS without LaTeX/weasyprint":

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
