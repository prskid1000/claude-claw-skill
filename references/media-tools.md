# Media Processing Tools Reference

> **TL;DR: use `claw img <verb>` / `claw media <verb>` for common tasks.** See [references/claw/img.md](claw/img.md) (Pillow + ImageMagick wrapper) and [references/claw/media.md](claw/media.md) (ffmpeg wrapper). This reference documents the Pillow Python API, the full ImageMagick flag / operator surface, and the full ffmpeg encoder / filter / codec matrix — the escape-hatch content `claw` deliberately doesn't wrap (per-channel math, morphology, filter chains, `-fx` expressions, complex filtergraphs, HDR tone-mapping, device capture, etc.).

## Contents

- **PROCESS images (Python)** — `Pillow`
  - [Supported formats](#11-supported-formats) · [Image modes](#12-image-modes) *(escape-hatch only)*
  - [Image class — all methods](#13-image-class----all-methods-and-properties) *(common ops covered by `claw img resize/crop/convert`)*
  - [ImageDraw — shapes/text](#14-imagedraw) · [ImageFont — TTF/OTF](#15-imagefont) *(drawing primitives — escape-hatch only; `claw img watermark` wraps the common text/logo case)*
  - [ImageFilter — blur/sharpen](#16-imagefilter) *(unsharp-mask covered by `claw img sharpen`)*
  - [ImageEnhance — brightness/contrast](#17-imageenhance) *(common ops covered by `claw img enhance`)*
  - [ImageOps — autocontrast/fit](#18-imageops) *(`autocontrast`/`equalize`/`fit`/`pad` covered by `claw img`)*
  - [ImageChops — channel ops](#19-imagechops-channel-operations) *(escape-hatch — not in `claw`)*
  - [Other modules (Stat, Grab, Sequence, Morph, Path, CMS, Color, Math)](#110-other-modules) *(escape-hatch only)*
- **PROCESS images (CLI)** — `ImageMagick`
  - [Core CLI tools (magick, identify, convert)](#21-core-cli-tools) · [Geometry syntax](#22-geometry-syntax) *(geometry strings flow straight through `claw img resize --geometry`)*
  - [Resize filters](#23-resize-filters) · [Format conversion](#24-format-conversion) *(covered by `claw img convert/to-jpeg/to-webp`)*
  - [Color operations](#25-color-operations) · [Drawing & text](#26-drawing-and-text) *(escape-hatch — flag DSL that `claw` won't wrap)*
  - [Effects & filters](#27-effects-and-filters) · [Compositing](#28-compositing) *(basic composite covered by `claw img composite/watermark`)*
  - [Distortions](#29-distortions) · [Morphology](#210-morphology) *(escape-hatch — not in `claw`)*
  - [Montage & batch](#211-montage-and-batch-processing) *(basic batch covered by `claw img batch`)*
  - [Animation](#212-animation) · [Image comparison](#213-image-comparison) *(frame → GIF covered by `claw img gif-from-frames`)*
  - [PDF operations](#214-pdf-operations) · [Metadata (EXIF/IPTC/XMP)](#215-metadata) *(EXIF read/strip/auto-rotate covered by `claw img exif`)*
  - [Miscellaneous operators](#216-miscellaneous-operators)
- **PROCESS video / audio** — `ffmpeg`
  - [Video codecs](#31-video-codecs) · [Audio codecs](#32-audio-codecs) · [Container formats](#33-container-formats) · [Rate control](#34-rate-control) *(common CRF presets covered by `claw media compress`)*
  - [Video filters (-vf)](#35-video-filters--vf---filterv) · [Audio filters (-af)](#36-audio-filters--af---filtera) *(basic scale/crop/overlay/loudnorm covered by `claw media scale/compress/loudnorm`)*
  - [Device capture](#37-device-capture) *(escape-hatch — not in `claw`)*
  - [Subtitles](#38-subtitles) *(burn-in covered by `claw media burn-subs`)*
  - [Image operations](#39-image-operations) *(frame extract / slideshow / GIF covered by `claw media thumbnail/gif`)*
  - [Advanced features (HW accel, streaming, complex filtergraphs)](#310-advanced-features) *(escape-hatch — not in `claw`)*
  - [ffprobe — inspect streams](#311-ffprobe) *(covered by `claw media info`)*
- **Escape-hatch recipes** — [Pillow channel math, morphology, complex filtergraphs, two-pass loudnorm, device capture](#escape-hatch-recipes)

---

# 1. Pillow (PIL) -- Python Image Manipulation

> **TL;DR: use `claw img <verb>` for everything in this section's covered branches.** See [references/claw/img.md](claw/img.md) — `resize`, `fit`, `pad`, `thumb`, `crop`, `enhance`, `sharpen`, `composite`, `watermark`, `overlay`, `convert`, `to-jpeg`, `to-webp`, `exif`, `rename`, `batch`, `gif-from-frames`. This section keeps only the API shape `claw img` doesn't wrap: full format-param catalog, mode catalog, resample / transform enums, `ImageDraw` primitives (freeform canvas), `ImageFont` variable-axis control, `ImageChops` channel math, `ImageMath` expression eval, and `ImageCms` ICC profiles.

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps, ImageChops, ImageStat, ImageGrab, ImageSequence, ImageMorph, ImagePath, ImageCms, ImageColor, ImageMath
```

---

## 1.1 Supported Formats

**Common R/W** (full support): PNG, JPEG, JPEG 2000, GIF (animated), BMP, TIFF (multi-page), WebP (animated), ICO (multi-size), PDF (write-only), EPS (needs Ghostscript), PPM, TGA, PCX, DDS (DXT1/3/5/BC5/BC7), IM, SGI, SPIDER, XBM, ICNS, MPO (stereoscopic), QOI, DIB, BLPS.

**Read-only**: FITS, XPM, MSP, FLI/FLC, BUFR, GRIB, HDF5, WMF/EMF, CUR, DCX, FTEX, GBR, GD, IMT, IPTC/NAA, MCIDAS, MIC, PCD, PIXAR, PSD (flattened composite), SUN, WAL.

**Write-only**: PALM.

Key save params by format:
- **JPEG**: `quality` (1-95), `progressive`, `optimize`, `subsampling` (0/1/2), `exif`, `icc_profile`.
- **PNG**: `optimize`, `compress_level` (0-9), `bits` (1/2/4/8), `transparency`, `icc_profile`.
- **WebP**: `quality` (1-100), `lossless`, `method` (0-6), `exact`, `icc_profile`.
- **GIF**: `save_all`, `append_images`, `duration` (ms), `loop` (0=infinite), `optimize`, `transparency`, `disposal` (0-3).
- **TIFF**: `compression` (`tiff_lzw`/`tiff_deflate`/`jpeg`/...), `dpi`, `resolution_unit`.
- **PDF**: `save_all`, `append_images`, `resolution`, `title`/`author`/`subject`/`keywords`/`creator`/`producer`.
- **ICO**: `sizes=[(16,16),(32,32),(48,48),(256,256)]`.

## 1.2 Image Modes

| Mode | Description | Pixel Type |
|------|-------------|------------|
| `1` | 1-bit bilevel (black/white) | bool |
| `L` | 8-bit grayscale | uint8 |
| `LA` | Grayscale + alpha | uint8 x2 |
| `La` | Grayscale + premultiplied alpha | uint8 x2 |
| `P` | 8-bit palette-mapped | uint8 (index) |
| `PA` | Palette + alpha | uint8 x2 |
| `RGB` | 24-bit true color | uint8 x3 |
| `RGBA` | RGB + alpha | uint8 x4 |
| `RGBa` | RGB + premultiplied alpha | uint8 x4 |
| `RGBX` | RGB + padding | uint8 x4 |
| `CMYK` | Cyan/Magenta/Yellow/Key | uint8 x4 |
| `YCbCr` | JPEG color space | uint8 x3 |
| `LAB` | CIE L*a*b* | uint8 x3 |
| `HSV` | Hue/Saturation/Value | uint8 x3 |
| `I` | 32-bit signed integer | int32 |
| `I;16` | 16-bit unsigned integer | uint16 |
| `I;16L` | 16-bit unsigned LE | uint16 |
| `I;16B` | 16-bit unsigned BE | uint16 |
| `I;16N` | 16-bit unsigned native endian | uint16 |
| `F` | 32-bit floating point | float32 |

## 1.3 Image Class -- All Methods and Properties

> `claw img resize | fit | pad | thumb | crop | convert | to-jpeg | to-webp | exif` cover the common ops — see [claw/img.md](claw/img.md). Below: construction API, resample / transpose / transform enums (for escape-hatch calls from your own code).

### Construction / save / close

- `Image.open(fp, mode="r", formats=None)` — file / path / URL / bytes
- `Image.new(mode, size, color=0)` — blank
- `Image.frombytes(mode, size, data, decoder="raw")` — from raw bytes
- `Image.frombuffer(mode, size, data)` — no-copy buffer wrap
- `Image.fromarray(obj, mode=None)` — from numpy
- `img.save(fp, format=None, **params)` — params per format in §1.1
- `img.copy()` · `img.close()` · `img.show(title=None)`

### Geometry methods

- `img.resize(size, resample=BICUBIC, box=None, reducing_gap=None)`
- `img.thumbnail(size, resample=BICUBIC, reducing_gap=2.0)` — in-place, preserves aspect
- `img.crop(box=(left, upper, right, lower))`
- `img.rotate(angle, resample=NEAREST, expand=False, center=None, translate=None, fillcolor=None)`
- `img.transpose(method)` (method enums below)
- `img.transform(size, method, data=None, resample=BICUBIC, fill=1, fillcolor=None)`
- `img.reduce(factor, box=None)` — integer downscale

### Resample algorithms (for `resize`, `rotate`, `transform`)

| Constant | Value | Quality | Speed |
|---|---|---|---|
| `Image.Resampling.NEAREST` | 0 | Lowest | Fastest |
| `Image.Resampling.BOX` | 4 | Low | Fast |
| `Image.Resampling.BILINEAR` | 2 | Medium | Medium |
| `Image.Resampling.HAMMING` | 5 | Medium+ | Medium |
| `Image.Resampling.BICUBIC` | 3 | High | Slow |
| `Image.Resampling.LANCZOS` | 1 | Highest | Slowest |

### Transpose methods

| Constant | Effect |
|---|---|
| `Image.Transpose.FLIP_LEFT_RIGHT` | Horizontal mirror |
| `Image.Transpose.FLIP_TOP_BOTTOM` | Vertical mirror |
| `Image.Transpose.ROTATE_90` | 90° CCW |
| `Image.Transpose.ROTATE_180` | 180° |
| `Image.Transpose.ROTATE_270` | 270° CCW |
| `Image.Transpose.TRANSPOSE` | Main diagonal |
| `Image.Transpose.TRANSVERSE` | Secondary diagonal |

### Transform methods

| Constant | Data | Description |
|---|---|---|
| `Image.Transform.AFFINE` | 6-tuple (a,b,c,d,e,f) | Affine |
| `Image.Transform.PERSPECTIVE` | 8-tuple | Perspective warp |
| `Image.Transform.QUAD` | 8-tuple (4 corners) | Map quad → rectangle |
| `Image.Transform.MESH` | list of `(box, quad)` | Piecewise transform |
| `Image.Transform.EXTENT` | 4-tuple (box) | Crop + scale |

### Compositing / merging

- `img.paste(im, box=None, mask=None)`
- `Image.alpha_composite(im1, im2)` — both RGBA
- `Image.composite(im1, im2, mask)` — composite via mask
- `Image.blend(im1, im2, alpha)` — linear interpolation
- `Image.merge(mode, bands)` · `img.split()`

### Mode conversion / quantize

- `img.convert(mode=None, matrix=None, dither=None, palette=Palette.WEB, colors=256)`
- `img.quantize(colors=256, method=None, kmeans=0, palette=None, dither=Dither.FLOYDSTEINBERG)`

Dither: `Dither.NONE` / `FLOYDSTEINBERG` / `ORDERED` / `RASTERIZE`.

Quantize methods: `Quantize.MEDIANCUT` (0), `MAXCOVERAGE` (1), `FASTOCTREE` (2), `LIBIMAGEQUANT` (3).

### Pixel / data access

`img.filter(kernel)` · `img.point(lut, mode=None)` · `img.getpixel((x,y))` · `img.putpixel((x,y), value)` · `img.load()` → `PixelAccess` · `img.getdata(band=None)` · `img.putdata(data, scale=1.0, offset=0.0)` · `img.tobytes(encoder_name="raw", *args)`.

### Introspection

`img.getbbox()` · `img.getcolors(maxcolors=256)` · `img.getextrema()` · `img.histogram(mask=None, extrema=None)` · `img.entropy(mask=None, extrema=None)`.

### Metadata / properties

`img.getexif()` · `img.getxmp()` · `img.info` (dict) · `img.format` · `img.mode` · `img.size` / `.width` / `.height` · `img.palette` (P mode) · `img.n_frames` · `img.is_animated`.

### Animation / multi-frame

`img.seek(frame)` · `img.tell()` · `img.n_frames`.

### Palette / miscellaneous

`img.draft(mode, size)` (JPEG loader speed) · `img.verify()` · `img.effect_spread(distance)` · `img.getpalette(mode="RGB")` · `img.putpalette(data, rawmode="RGB")` · `img.remap_palette(dest_map, source_palette=None)`.

## 1.4 ImageDraw

Escape hatch — `claw img watermark` handles the common "stamp text / logo" case; any freeform drawing (shapes, diagrams, custom charts) uses this API directly.

```python
from PIL import ImageDraw
draw = ImageDraw.Draw(im, mode=None)
```

### Drawing primitives

| Call | Signature |
|---|---|
| `line` | `draw.line(xy, fill=None, width=0, joint=None)` — `joint=None` or `"curve"` |
| `rectangle` | `draw.rectangle(xy, fill, outline, width=1)` |
| `rounded_rectangle` | `draw.rounded_rectangle(xy, radius, fill, outline, width=1, corners=(tl,tr,br,bl))` |
| `ellipse` | `draw.ellipse(xy, fill, outline, width=1)` — `xy` = bounding box |
| `polygon` | `draw.polygon(xy, fill, outline, width=1)` |
| `regular_polygon` | `draw.regular_polygon(bounding_circle, n_sides, rotation=0, fill, outline, width=1)` |
| `arc` | `draw.arc(xy, start, end, fill, width=0)` — degrees, 0=3 o'clock CCW |
| `chord` | `draw.chord(xy, start, end, fill, outline, width=1)` |
| `pieslice` | `draw.pieslice(xy, start, end, fill, outline, width=1)` |
| `point` | `draw.point(xy, fill)` |
| `circle` | `draw.circle(xy, radius, fill, outline, width=1)` — `xy` = center |
| `bitmap` | `draw.bitmap(xy, bitmap, fill)` — bitmap is mode "1" image |

`xy` coord format: `[(x1,y1),(x2,y2),...]` or flat `[x1,y1,x2,y2,...]`.

### Text rendering

```python
draw.text(xy, text, fill=None, font=None, anchor=None, spacing=4, align="left",
          direction=None, features=None, language=None,
          stroke_width=0, stroke_fill=None, embedded_color=False)
```

`anchor` — 2-char string: horizontal `l`/`m`/`r`/`s`, vertical `a`/`t`/`m`/`s`/`b`/`d`.
`align` — `"left"` / `"center"` / `"right"` (multiline only).
`direction` — `"rtl"` / `"ltr"` / `"ttb"` (requires libraqm).

Also: `draw.multiline_text(...)`, `draw.textlength(...)`, `draw.textbbox(xy, text, font, anchor, spacing, align, direction, features, language, stroke_width)` → `(l, t, r, b)`, `draw.multiline_textbbox(...)`, `draw.multiline_textlength(...)`.

### Flood fill

`ImageDraw.floodfill(image, xy, value, border=None, thresh=0)`.

## 1.5 ImageFont

Escape hatch — `claw img watermark` accepts a `--font` path + size; any variable-axis control, font-metrics lookup, or transposed-font work goes through this API.

`ImageFont.truetype(font, size=10, index=0, encoding="", layout_engine=None)` — layout engines: `ImageFont.Layout.BASIC` or `RAQM`.

`ImageFont.load_default(size=None)` — built-in bitmap (size param requires Pillow ≥ 10.1).

`ImageFont.TransposedFont(font, orientation=None)` — rotated font wrapper.

FreeTypeFont methods:

- `font.getbbox(text, mode, direction, features, language, stroke_width, anchor)`
- `font.getlength(text, mode, direction, features, language)`
- `font.getmask(...)` / `font.getmask2(...)` → `(mask_image, offset)`
- `font.getmetrics()` → `(ascent, descent)`
- `font.get_variation_names()` / `font.get_variation_axes()` — variable font introspection
- `font.set_variation_by_name(name)` / `font.set_variation_by_axes(axes)`

## 1.6 ImageFilter

> `claw img sharpen` wraps `UnsharpMask`; `--op blur:N` wraps `GaussianBlur`. See [claw/img.md](claw/img.md).

Apply via `img.filter(ImageFilter.PRESET)`:

| Preset | Effect |
|---|---|
| `BLUR` | Uniform 5×5 blur |
| `CONTOUR` | Edge contours |
| `DETAIL` | Detail enhancement |
| `EDGE_ENHANCE` | Light edge enhancement |
| `EDGE_ENHANCE_MORE` | Strong edge enhancement |
| `EMBOSS` | Emboss |
| `FIND_EDGES` | Edge detection |
| `SHARPEN` | Sharpen |
| `SMOOTH` | Light smoothing |
| `SMOOTH_MORE` | Strong smoothing |

Parameterized classes:

- `ImageFilter.GaussianBlur(radius=2)`
- `ImageFilter.BoxBlur(radius)`
- `ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3)`
- `ImageFilter.Kernel(size, kernel, scale=None, offset=0)` — size `(w, h)`; kernel flat list; scale auto if None
- `ImageFilter.RankFilter(size, rank)` — size = kernel, rank = sorted pixel index
- `ImageFilter.MedianFilter(size=3)` ≡ `RankFilter(size, size*size//2)`
- `ImageFilter.MinFilter(size=3)` ≡ `RankFilter(size, 0)`
- `ImageFilter.MaxFilter(size=3)` ≡ `RankFilter(size, size*size-1)`
- `ImageFilter.ModeFilter(size=3)` — most common pixel in neighborhood

## 1.7 ImageEnhance

> `claw img enhance [--brightness N --color N --contrast N --sharpness N]` wraps all four — see [claw/img.md](claw/img.md).

Interface: `ImageEnhance.<Class>(image).enhance(factor)`. `factor`: 0.0 = minimum, 1.0 = original, 2.0 = doubled effect.

| Class | factor=0.0 | factor=1.0 | factor=2.0 |
|---|---|---|---|
| `Brightness` | Black | Original | 2× brightness |
| `Color` | Grayscale | Original | 2× saturation |
| `Contrast` | Solid gray | Original | 2× contrast |
| `Sharpness` | Blurred | Original | 2× sharpened |

## 1.8 ImageOps

> `claw img enhance --autocontrast|--equalize|--posterize|--solarize|--invert` and `claw img fit|pad|thumb|crop` wrap the common cases — see [claw/img.md](claw/img.md). Below: the full function list for in-code escape-hatch use.

| Function | Purpose |
|---|---|
| `autocontrast(img, cutoff=0, ignore=None, mask=None, preserve_tone=False)` | Maximize dynamic range |
| `colorize(img, black, white, mid=None, blackpoint=0, whitepoint=255, midpoint=127)` | Grayscale → two/three-color gradient |
| `contain(img, size, method=BICUBIC)` | Fit inside size, preserve aspect |
| `cover(img, size, method=BICUBIC)` | Cover size, preserve aspect (may crop) |
| `crop(img, border=0)` | Remove border pixels |
| `deform(img, deformer, resample=BILINEAR)` | Deformer object w/ `getmesh()` |
| `equalize(img, mask=None)` | Histogram equalization |
| `expand(img, border=0, fill=0)` | Add border (int or `(l,t,r,b)`) |
| `exif_transpose(img, in_place=False)` | Auto-rotate per EXIF orientation |
| `fit(img, size, method=BICUBIC, bleed=0.0, centering=(0.5, 0.5))` | Crop + resize to exact size |
| `flip(img)` | Vertical flip |
| `grayscale(img)` | To grayscale |
| `invert(img)` | Invert colors |
| `mirror(img)` | Horizontal flip |
| `pad(img, size, method=BICUBIC, color=None, centering=(0.5, 0.5))` | Resize + letterbox |
| `posterize(img, bits)` | Reduce to N bits / channel |
| `scale(img, factor, resample=BICUBIC)` | Scale by factor |
| `solarize(img, threshold=128)` | Invert pixels above threshold |

## 1.9 ImageChops (Channel Operations)

```python
from PIL import ImageChops
```

All functions take two images and return a new image unless noted:

```python
ImageChops.add(im1, im2, scale=1.0, offset=0)        # (im1 + im2) / scale + offset
ImageChops.add_modulo(im1, im2)                       # (im1 + im2) % 256
ImageChops.subtract(im1, im2, scale=1.0, offset=0)   # (im1 - im2) / scale + offset
ImageChops.subtract_modulo(im1, im2)                  # (im1 - im2) % 256
ImageChops.multiply(im1, im2)                         # im1 * im2 / 255
ImageChops.screen(im1, im2)                           # 255 - ((255-im1) * (255-im2) / 255)
ImageChops.overlay(im1, im2)                          # Overlay blend
ImageChops.soft_light(im1, im2)                       # Soft light blend
ImageChops.hard_light(im1, im2)                       # Hard light blend
ImageChops.difference(im1, im2)                       # |im1 - im2|
ImageChops.darker(im1, im2)                           # min(im1, im2)
ImageChops.lighter(im1, im2)                          # max(im1, im2)
ImageChops.constant(image, value)                     # Fill with constant value
ImageChops.duplicate(image)                           # Copy
ImageChops.invert(image)                              # 255 - pixel
ImageChops.offset(image, xoffset, yoffset=None)       # Shift image, wrap around
ImageChops.logical_and(im1, im2)                      # Bitwise AND
ImageChops.logical_or(im1, im2)                       # Bitwise OR
ImageChops.logical_xor(im1, im2)                      # Bitwise XOR
```

## 1.10 Other Modules

All escape-hatch — `claw` doesn't wrap these.

### ImageStat

`stat = ImageStat.Stat(image, mask=None)` — per-band lists: `.extrema`, `.count`, `.sum`, `.sum2`, `.mean`, `.median`, `.rms`, `.var`, `.stddev`.

### ImageGrab

- `ImageGrab.grab(bbox=None, include_layered_windows=False, all_screens=False, xdisplay=None)` — screenshot; `bbox=(l, t, r, b)`.
- `ImageGrab.grabclipboard()` — returns Image or list of file paths.

### ImageSequence

```python
for frame in ImageSequence.Iterator(im):    # animated image frame iterator
    ...
```

### ImageMorph

```python
lut = ImageMorph.LutBuilder(patterns=None, op_name=None)
# op_name: "erosion4" / "erosion8" / "dilation4" / "dilation8" / "edge"
lut.build_lut()
mop = ImageMorph.MorphOp(lut=None, op_name=None, patterns=None)
count, outimage = mop.apply(image)
count = mop.match(image)
mop.get_on_pixels(image)
```

### ImagePath

`path = ImagePath.Path(coords)` (list of `(x, y)` or flat `[x1,y1,x2,y2,...]`). Methods: `.compact(distance=2)`, `.getbbox()`, `.map(function)`, `.tolist(flat=0)`, `.transform(matrix)` (6-tuple affine or `(a,b,c,d)` 2×2).

### ImageCms (ICC Color Management)

- `ImageCms.buildTransform(inputProfile, outputProfile, inMode, outMode, renderingIntent=0, flags=0)`
- `ImageCms.applyTransform(im, transform, inPlace=False)`
- `ImageCms.profileToProfile(im, inputProfile, outputProfile, renderingIntent=0, outputMode=None, inPlace=False, flags=0)`
- `ImageCms.createProfile(colorSpace, colorTemp=-1)` — `"sRGB"` / `"Lab"` / `"XYZ"`
- `ImageCms.getOpenProfile(file)` · `getProfileName` · `getProfileDescription` · `getProfileInfo`

Rendering intents: `ImageCms.Intent.PERCEPTUAL` (0), `RELATIVE_COLORIMETRIC` (1), `SATURATION` (2), `ABSOLUTE_COLORIMETRIC` (3).

### ImageColor

`ImageColor.getrgb(color)` → `(R, G, B)` / `(R, G, B, A)`. `ImageColor.getcolor(color, mode)` → mode-appropriate tuple.

Accepted formats: `"#rgb"` · `"#rrggbb"` · `"#rrggbbaa"` · `"rgb(r,g,b)"` · `"rgb(r%,g%,b%)"` · `"hsl(h,s%,l%)"` · `"hsv(h,s%,v%)"` · CSS3 names (`"red"`, `"cornflowerblue"`, …).

### ImageMath

```python
ImageMath.eval(expression, **environment)
# Supply images as keyword args. Operators: + - * / % ** & | ^ ~ >> <<
# Functions: abs, min, max, int, float, convert(mode)
# Comparisons return 0/255 images.
ImageMath.lambda_eval(function, **environment)        # Python-lambda variant
```

---

# 2. ImageMagick (magick CLI)

Command syntax: `magick [input...] [operations...] [output]`

---

## 2.1 Core CLI Tools

| Command | Purpose |
|---------|---------|
| `magick` | Primary tool -- convert, process, create images |
| `magick mogrify` | Batch in-place modification |
| `magick montage` | Create contact sheets / image grids |
| `magick identify` | Print image metadata and properties |
| `magick compare` | Compute and visualize image differences |
| `magick composite` | Composite two images together |
| `magick stream` | Stream pixel data from image (low memory) |
| `magick animate` | Animate image sequence (X11) |
| `magick display` | Display image (X11) |
| `magick import` | Screen capture (X11) |

## 2.2 Geometry Syntax

```
WxH        Resize to fit within WxH, preserve aspect ratio
WxH!       Force exact dimensions (distort if needed)
WxH>       Shrink only if larger than WxH
WxH<       Enlarge only if smaller than WxH
WxH^       Resize to fill WxH (minimum dimension match, may overflow)
W           Width only, auto height
xH          Height only, auto width
scale%      Scale by percentage (e.g., 50%)
scale-x%xscale-y%   Independent axis scaling
@area       Resize to fit within total pixel area
WxH+X+Y    Geometry with offset (crop, extent, etc.)
WxH-X-Y    Geometry with negative offset
```

## 2.3 Resize Filters

Specify with `-filter <name> -resize WxH`:

| Filter | Best For |
|--------|----------|
| Lanczos | General high-quality downscale (default) |
| Mitchell | General purpose, balanced |
| Catrom | Sharpening, Catmull-Rom spline |
| Cubic | Cubic interpolation |
| Gaussian | Smooth, less aliasing |
| Triangle | Bilinear interpolation |
| Point | Nearest-neighbor (pixel art) |
| Hermite | Smooth interpolation |
| Hanning | Windowed sinc |
| Hamming | Windowed sinc variant |
| Blackman | Windowed sinc, less ringing |
| Kaiser | Windowed sinc, adjustable |
| Welsh | Parabolic window |
| Parzen | Cubic approximation |
| Bohman | Cosine-weighted window |
| Bartlett | Triangular window |
| Lagrange | Lagrange interpolation |
| Sinc | Ideal lowpass (truncated) |
| SincFast | Optimized sinc |

Alternate resize operators:
```
-resize WxH           Standard resize
-adaptive-resize WxH  Data-dependent triangulation resize (no blur)
-scale WxH            Simple pixel sampling (fastest)
-sample WxH           Point sampling (nearest-neighbor)
-magnify               Double size via pixel replication
-liquid-rescale WxH   Seam carving (content-aware resize)
-thumbnail WxH        Optimized resize for thumbnails (strip metadata)
-extent WxH           Set canvas size (crop or expand)
```

## 2.4 Format Conversion

200+ supported formats. Convert by specifying output extension:

```bash
magick input.png output.jpg
magick input.svg -density 300 output.png    # Rasterize vector at 300 DPI
magick input.pdf[0] output.png              # Extract page 0 from PDF
magick input.pdf output-%03d.png            # All pages to numbered PNGs
magick *.jpg output.pdf                     # Multiple images to multi-page PDF
magick input.png -define webp:lossless=true output.webp
```

Key format-specific options:
- **JPEG**: `-quality 1-100`, `-sampling-factor 4:2:0`, `-interlace Plane` (progressive)
- **PNG**: `-quality 00-99` (zlib compression + filter), `-define png:compression-level=9`
- **WebP**: `-quality 0-100`, `-define webp:lossless=true`, `-define webp:method=6`
- **TIFF**: `-compress LZW|ZIP|JPEG|None`, `-define tiff:tile-geometry=256x256`
- **GIF**: `-layers optimize`, `-coalesce`, `-fuzz N%` (color matching tolerance)
- **HEIC**: `-quality 0-100`
- **AVIF**: `-quality 0-100`
- **PDF**: `-density DPI`, `-page Letter|A4|...`

## 2.5 Color Operations

```bash
-brightness-contrast BxC       # B: brightness (-100 to +100), C: contrast (-100 to +100)
-modulate B,S,H                # B: brightness%, S: saturation%, H: hue rotation (100=unchanged)
-gamma value                   # Gamma correction (1.0=unchanged, <1=darker, >1=lighter)
-gamma R,G,B                   # Per-channel gamma
-level black%,white%[,gamma]   # Input level adjustment
-level-colors black,white      # Map black/white to specified colors
-auto-level                    # Stretch to full dynamic range
-normalize                     # Stretch to full range (robust, ignores 2% outliers)
-equalize                      # Histogram equalization
-linear-stretch black%xwhite%  # Linear stretch with clipping percentages
-contrast-stretch black%xwhite%  # Stretch with pixel count clipping
-sigmoidal-contrast C,M%       # S-curve contrast (C=strength 0-20, M=midpoint)
+sigmoidal-contrast C,M%       # Inverse sigmoidal contrast (lighten shadows)
-negate                        # Invert all colors
+negate                        # Invert only non-alpha channels
-threshold value%              # Binary threshold
-white-threshold value%        # Set pixels above threshold to white
-black-threshold value%        # Set pixels below threshold to black
-colorize value%               # Blend with fill color at given percentage
-tint value%                   # Tint midtones with fill color
-grayscale method              # Methods: Rec601Luma, Rec709Luma, Brightness, Lightness, Average, RMS
-sepia-tone threshold%         # Sepia tone effect
-colorspace name               # Convert color space (sRGB, RGB, CMYK, Gray, HSL, HSB, Lab, etc.)
-color-matrix "rows x cols: values"  # Apply color matrix transform
```

## 2.6 Drawing and Text

### MVG Drawing Primitives (-draw)

```bash
-draw "point x,y"
-draw "line x1,y1 x2,y2"
-draw "rectangle x1,y1 x2,y2"
-draw "roundrectangle x1,y1 x2,y2 rx,ry"
-draw "circle cx,cy edge_x,edge_y"
-draw "ellipse cx,cy rx,ry start,end"
-draw "arc x1,y1 x2,y2 start,end"
-draw "polyline x1,y1 x2,y2 x3,y3 ..."
-draw "polygon x1,y1 x2,y2 x3,y3 ..."
-draw "bezier x1,y1 x2,y2 x3,y3 x4,y4"
-draw "path 'M x,y L x2,y2 C cx1,cy1 cx2,cy2 x3,y3 Z'"  # SVG path syntax
-draw "text x,y 'string'"
-draw "image Over x,y w,h 'filename'"
-draw "rotate degrees"
-draw "translate dx,dy"
-draw "scale sx,sy"
-draw "skewX degrees"
-draw "skewY degrees"
```

Drawing settings (apply before -draw):
```bash
-fill color              # Fill color
-stroke color            # Stroke color
-strokewidth N           # Stroke width in pixels
-font name               # Font face name or path
-pointsize N             # Text size in points
-gravity position        # NorthWest|North|NorthEast|West|Center|East|SouthWest|South|SouthEast
```

### Text Annotation

```bash
-annotate +X+Y "text"               # Place text at offset, supports angle: -annotate 30x0+X+Y
-annotate angle "text"               # Rotated text
-caption "text"                      # Fit text within image bounds (auto word-wrap/resize)
-label "text"                        # Set label metadata (used by montage)
```

Text formatting options:
```bash
-font path/to/font.ttf
-family "Font Family"
-style Normal|Italic|Oblique
-weight 100-900|Bold
-pointsize N
-fill color                          # Text color
-stroke color                        # Text outline color
-strokewidth N
-undercolor color                    # Background behind text
-gravity position
-kerning N                           # Letter spacing adjustment
-interline-spacing N                 # Line spacing adjustment
-interword-spacing N                 # Word spacing adjustment
-direction right-to-left|left-to-right
```

Pango markup (with `pango:` prefix):
```bash
magick -size 400x200 pango:"<b>Bold</b> <i>Italic</i> <span foreground='red'>Red</span>" output.png
```

## 2.7 Effects and Filters

```bash
# Blur
-blur 0xSigma                       # Gaussian blur (0=auto radius)
-gaussian-blur 0xSigma              # True Gaussian blur
-motion-blur 0xSigma+angle          # Directional motion blur
-radial-blur angle                  # Rotational blur
-adaptive-blur 0xSigma              # Edge-preserving blur
-bilateral-blur widthxheight+intensity+spatial  # Edge-preserving bilateral

# Sharpen
-sharpen 0xSigma                    # Unsharp-mask style sharpen
-adaptive-sharpen 0xSigma           # Edge-adaptive sharpen
-unsharp 0xSigma+amount+threshold   # Unsharp mask (amount=%, threshold=0-1)

# Artistic
-emboss radius                      # Emboss effect
-edge radius                        # Edge detection
-charcoal radius                    # Charcoal sketch effect
-sketch 0xSigma+angle               # Pencil sketch
-oil-paint radius                   # Oil painting effect
-paint radius                       # Coarser oil painting
-spread amount                      # Random displacement of pixels
-kuwahara radius                    # Kuwahara anisotropic diffusion
-vignette 0xSigma                   # Darkened edges vignette

# Noise
-noise radius                       # Reduce noise (when no + prefix)
+noise type                         # Add noise: Gaussian|Impulse|Laplacian|Multiplicative|Poisson|Uniform
-median radius                      # Median filter
-statistic type WxH                 # Statistic filter: Gradient|Maximum|Mean|Median|Minimum|Mode|Nonpeak|RootMeanSquare|StandardDeviation

# Computer Vision
-morphology method:iterations kernel   # Morphological operations (see 2.10)
-connected-components connectivity     # Connected component labeling (4 or 8)
-canny 0xSigma+lower%+upper%          # Canny edge detector
-hough-lines WxH+threshold            # Hough line detection
```

## 2.8 Compositing

Syntax: `magick base overlay -composite` or `-compose operator -composite`

53 compositing operators (specify with `-compose`):

| Category | Operators |
|----------|-----------|
| Porter-Duff | Over, In, Out, Atop, Xor, Dst, DstOver, DstIn, DstOut, DstAtop, Src, Clear |
| Arithmetic | Plus, Minus, Add, Subtract, Difference, Exclusion |
| Blend | Multiply, Screen, Overlay, HardLight, SoftLight, PegtopLight, LinearLight, VividLight, PinLight, HardMix |
| Dodge/Burn | ColorDodge, ColorBurn, LinearDodge, LinearBurn |
| Lighten/Darken | Lighten, Darken, LightenIntensity, DarkenIntensity |
| Dissolve | Dissolve, Blend |
| Color | Hue, Saturate, Luminize, Colorize |
| Math | ModulusAdd, ModulusSubtract, Divide, MinusDst, MinusSrc |
| Special | CopyAlpha, CopyRed, CopyGreen, CopyBlue, ChangeMask, Displace, Distort, Blur |

```bash
magick base.png overlay.png -gravity Center -compose Over -composite output.png
magick base.png overlay.png -geometry +10+20 -compose Multiply -composite output.png
magick base.png -fill "rgba(0,0,0,0.5)" -draw "rectangle 0,0 100,100" output.png
```

## 2.9 Distortions

```bash
-distort method "parameters"
```

| Method | Parameters | Description |
|--------|------------|-------------|
| Affine | x1,y1 x1',y1' x2,y2 x2',y2' ... | Point-mapped affine |
| AffineProjection | sx,rx,ry,sy,tx,ty | Direct affine matrix |
| Perspective | x1,y1 x1',y1' x2,y2 x2',y2' x3,y3 x3',y3' x4,y4 x4',y4' | 4-point perspective |
| PerspectiveProjection | sx,ry,tx,rx,sy,ty,px,py | Direct 3x3 matrix |
| BilinearForward | x1,y1 x1',y1' ... (4 points) | Forward bilinear |
| BilinearReverse | x1,y1 x1',y1' ... (4 points) | Reverse bilinear |
| Polynomial | order x1,y1 x1',y1' ... | Polynomial fit |
| Arc | angle [rotate [top_radius [bottom_radius]]] | Bend into arc |
| Polar | Rmax [Rmin [Cx,Cy]] | Cartesian to polar |
| DePolar | 0 | Polar to Cartesian |
| Barrel | A B C D [X Y] | Barrel/pincushion distortion |
| BarrelInverse | A B C D | Inverse barrel |
| Cylinder2Plane | fov | Cylindrical projection to plane |
| Plane2Cylinder | fov | Plane to cylindrical projection |
| Shepards | x1,y1 x1',y1' ... | Shepard's distortion (rubber sheet) |
| ScaleRotateTranslate | [x,y] angle [scale] [newx,newy] | Combined SRT |
| Resize | - | Distort-based resize (virtual-pixel aware) |

Additional flags:
```bash
-virtual-pixel method              # Background: Undefined|Background|Edge|Mirror|Tile|Transparent|...
+distort method "params"           # Best-fit output size (auto viewport)
```

## 2.10 Morphology

```bash
-morphology method[:iterations] kernel
```

**Methods:**

| Category | Methods |
|----------|---------|
| Basic | Dilate, Erode, Open, Close, Smooth |
| Edge | EdgeIn, EdgeOut, Edge |
| TopHat | TopHat, BottomHat |
| Hit-and-Miss | HitAndMiss, Thinning, Thicken |
| Distance | Distance, Voronoi, IterativeDistance |
| Convolution | Convolve, Correlate |

**Built-in Kernels:**

| Category | Kernels |
|----------|---------|
| Convolution | Unity, Gaussian, DoG, LoG, Blur, Comet |
| Edge detection | Laplacian, Sobel, Roberts, Prewitt, Compass, Kirsch, FreiChen |
| Shape | Diamond, Square, Octagon, Disk, Plus, Cross, Ring, Rectangle |
| Distance | Chebyshev, Manhattan, Octagonal, Euclidean |
| Skeleton/Thin | Peaks, Edges, Corners, Diagonals, LineEnds, LineJunctions, Ridges, ConvexHull, Skeleton, ThinSE |

```bash
# Examples
magick input.png -morphology Erode Diamond:3 output.png
magick input.png -morphology EdgeIn Diamond output.png
magick input.png -morphology Distance Euclidean output.png
magick input.png -morphology Convolve Gaussian:0x2 output.png
```

## 2.11 Montage and Batch Processing

### Montage

```bash
magick montage input1.png input2.png input3.png [options] output.png
```

| Option | Description |
|--------|-------------|
| `-geometry WxH+Bx+By` | Tile size and border spacing |
| `-tile CxR` | Grid layout (columns x rows) |
| `-frame WxH+outer+inner` | Decorative frame around each tile |
| `-shadow` | Drop shadow under each tile |
| `-background color` | Background color |
| `-label "text"` | Label per image (supports `%f` filename, `%w` width, etc.) |
| `-title "text"` | Overall title |
| `-font name -pointsize N` | Label font settings |
| `-texture filename` | Background texture |
| `-mode Frame|Unframe|Concatenate` | Montage mode |

### Mogrify (Batch In-Place)

```bash
magick mogrify -resize 800x600 -quality 85 *.jpg                 # Resize all JPEGs in-place
magick mogrify -format png -path ./converted *.jpg                # Convert all to PNG, save in ./converted
magick mogrify -strip -auto-orient -resize "1920x1920>" *.jpg     # Normalize photos
```

## 2.12 Animation

```bash
# Create animated GIF from frames
magick -delay 100 -loop 0 frame*.png animated.gif    # delay in 1/100ths second

# Optimize animated GIF
magick input.gif -layers optimize output.gif

# Inter-frame morphing
magick image1.png image2.png -morph 10 morph_%03d.png

# Animation layer operations
-delay ticks[xticks-per-second]   # Frame delay (default tps=100)
-loop count                       # Loop count (0=infinite)
-dispose method                   # None|Background|Previous
-coalesce                         # Expand optimized frames to full size
-layers optimize                  # Optimize frame differences
-layers OptimizePlus              # More aggressive optimization
-layers OptimizeTransparency      # Transparency optimization
-layers compare                   # Compare layers
-layers composite                 # Composite layer sequences
-layers merge                     # Merge visible layers
-layers flatten                   # Flatten to single layer
-layers mosaic                    # Mosaic all layers
-layers trim                      # Trim each layer
-layers remove-dups               # Remove duplicate frames
-morph N                          # Insert N morph frames between each pair
```

## 2.13 Image Comparison

```bash
magick compare image1.png image2.png diff.png              # Visual diff
magick compare -metric RMSE image1.png image2.png null:    # Numeric diff only
```

| Metric | Description |
|--------|-------------|
| AE | Absolute Error (pixel count that differ) |
| DSSIM | Structural Dissimilarity (1-SSIM) |
| Fuzz | Mean color distance |
| MAE | Mean Absolute Error |
| MEPP | Mean Error Per Pixel |
| MSE | Mean Squared Error |
| NCC | Normalized Cross Correlation |
| PAE | Peak Absolute Error |
| PHASH | Perceptual Hash distance |
| PSNR | Peak Signal-to-Noise Ratio (dB) |
| RMSE | Root Mean Squared Error |
| SSIM | Structural Similarity Index (1.0 = identical) |

```bash
-fuzz N%              # Color tolerance for AE comparison
-highlight-color      # Color for different pixels
-lowlight-color       # Color for similar pixels
-subimage-search      # Find subimage within larger image
-dissimilarity-threshold N  # Threshold for subimage search
```

## 2.14 PDF Operations

```bash
magick -density 300 input.pdf output.png            # Rasterize at 300 DPI
magick -density 300 input.pdf[0-4] page_%d.png      # Pages 0-4
magick -density 300 input.pdf[0] -quality 95 out.jpg # Single page to JPEG
magick *.png -adjoin output.pdf                      # Images to multi-page PDF
magick input.pdf -resize 50% output.pdf              # Resize PDF pages
```

## 2.15 Metadata

```bash
magick identify image.png                            # Basic info
magick identify -verbose image.png                   # Full metadata dump
magick identify -format "%wx%h %m %b" image.png      # Custom format

# Format escapes: %w=width, %h=height, %m=format, %b=filesize, %z=depth,
# %k=unique_colors, %n=number_of_images, %p=page_number, %x/%y=resolution

-set property value                                  # Set metadata
-strip                                               # Remove all metadata
-profile filename                                    # Apply ICC/IPTC profile
+profile "*"                                         # Remove all profiles
-profile filename                                    # Embed ICC profile
```

## 2.16 Miscellaneous Operators

```bash
-alpha Set|Off|On|Copy|Extract|Opaque|Transparent|Shape|Remove|Background|Activate|Deactivate
-background color
-bordercolor color
-border WxH
-channel RGBA                          # Channel selection for subsequent operations
-define format:option=value            # Format-specific settings
-density DPI                           # Resolution
-depth N                               # Bit depth (8, 16, 32)
-deskew threshold%                     # Auto-straighten scanned images
-fuzz N%                               # Color matching tolerance
-gravity position                      # Positioning anchor
-page WxH+X+Y                         # Virtual canvas size/offset
-repage WxH+X+Y                       # Reset virtual canvas
-rotate degrees                        # Rotate image
-crop WxH+X+Y                         # Crop region
-trim                                  # Auto-crop whitespace
+repage                                # Reset page geometry after crop
-flip                                  # Vertical mirror
-flop                                  # Horizontal mirror
-transpose                             # Mirror along top-left to bottom-right diagonal
-transverse                            # Mirror along top-right to bottom-left diagonal
-unique-colors                         # List unique colors
-type TrueColor|Grayscale|Palette|...  # Set image type
```

---

# 3. FFmpeg -- Audio/Video/Multimedia

General syntax:
```bash
ffmpeg [global_options] {[input_options] -i input}... {[output_options] output}...
```

---

## 3.1 Video Codecs

### Software Encoders

| Codec | Encoder | Typical Use |
|-------|---------|-------------|
| H.264/AVC | libx264 | Universal playback, streaming, web |
| H.265/HEVC | libx265 | Higher compression, 4K/HDR |
| VP8 | libvpx | WebM legacy |
| VP9 | libvpx-vp9 | WebM, YouTube, HDR |
| AV1 | libaom-av1 | Highest compression (slow encode) |
| AV1 | libsvtav1 | AV1 fast encoder (recommended) |
| AV1 | librav1e | AV1 Rust encoder |
| ProRes | prores_ks | Professional video editing (profiles 0-5) |
| DNxHD/DNxHR | dnxhd | Avid editing workflow |
| FFV1 | ffv1 | Lossless archival |
| Theora | libtheora | Open-source legacy |
| MPEG-4 ASP | libxvid | Legacy DivX/Xvid |
| MJPEG | mjpeg | Motion JPEG |
| PNG frames | png | Lossless frame sequences |
| GIF | gif | Animated GIF output |
| WebP | libwebp | Animated WebP |
| JPEG XL | libjxl | Next-gen image/animation format |

### Hardware-Accelerated Encoders

| Platform | H.264 | HEVC | AV1 |
|----------|-------|------|-----|
| NVIDIA (NVENC) | h264_nvenc | hevc_nvenc | av1_nvenc |
| Intel (QSV) | h264_qsv | hevc_qsv | av1_qsv |
| AMD (VAAPI/Linux) | h264_vaapi | hevc_vaapi | av1_vaapi |
| AMD (AMF/Windows) | h264_amf | hevc_amf | -- |
| Apple (VideoToolbox) | h264_videotoolbox | hevc_videotoolbox | -- |

## 3.2 Audio Codecs

| Codec | Encoder | Typical Use |
|-------|---------|-------------|
| AAC | aac | Default MP4/M4A audio |
| AAC | libfdk_aac | High-quality AAC (requires non-free build) |
| MP3 | libmp3lame | Universal lossy audio |
| Opus | libopus | Best lossy codec, low-latency, VoIP |
| Vorbis | libvorbis | OGG/WebM audio |
| FLAC | flac | Lossless compression |
| PCM 16-bit LE | pcm_s16le | Uncompressed CD-quality WAV |
| PCM 24-bit LE | pcm_s24le | Uncompressed high-res WAV |
| PCM 32-bit LE | pcm_s32le | Uncompressed 32-bit WAV |
| PCM 32-bit float | pcm_f32le | Floating-point WAV |
| AC-3 | ac3 | Dolby Digital |
| E-AC-3 | eac3 | Dolby Digital Plus |
| ALAC | alac | Apple Lossless (M4A/MOV) |
| WavPack | wavpack | Lossless with lossy hybrid mode |
| AMR-NB | amr_nb | Narrowband speech |
| AMR-WB | amr_wb | Wideband speech |

## 3.3 Container Formats

### Video Containers

| Format | Extension | Video Codecs | Audio Codecs | Notes |
|--------|-----------|-------------|-------------|-------|
| MP4 | .mp4, .m4v | H.264, H.265, AV1, VP9 | AAC, AC3, EAC3, Opus, FLAC | Universal playback |
| MKV | .mkv | Nearly all | Nearly all | Most flexible container |
| WebM | .webm | VP8, VP9, AV1 | Vorbis, Opus | Web-native |
| MOV | .mov | H.264, H.265, ProRes | AAC, PCM, ALAC | Apple QuickTime |
| AVI | .avi | Most legacy codecs | MP3, PCM, AC3 | Legacy, no modern codecs |
| FLV | .flv | H.264, VP6, Sorenson | AAC, MP3 | Flash legacy |
| MPEG-TS | .ts, .m2ts | H.264, H.265, MPEG-2 | AAC, AC3, MP2 | Broadcasting, streaming |
| OGG | .ogg, .ogv | Theora, VP8 | Vorbis, Opus, FLAC | Open-source |
| WMV | .wmv | WMV1/2/3, VC-1 | WMA | Windows Media |
| 3GP | .3gp | H.263, H.264 | AMR, AAC | Mobile legacy |
| MXF | .mxf | MPEG-2, DNxHD, ProRes | PCM | Professional broadcast |
| NUT | .nut | All FFmpeg codecs | All FFmpeg codecs | FFmpeg native container |

### Audio-Only Containers

| Format | Extension | Codec | Notes |
|--------|-----------|-------|-------|
| WAV | .wav | PCM, ADPCM | Uncompressed standard |
| FLAC | .flac | FLAC | Lossless |
| MP3 | .mp3 | MP3 | Universal lossy |
| AAC | .aac, .m4a | AAC | Advanced Audio Coding |
| OGG | .ogg | Vorbis, Opus | Open-source |
| WMA | .wma | WMA | Windows Media Audio |
| AIFF | .aiff | PCM | Apple uncompressed |

### Streaming Protocols

| Protocol | URL Scheme | Direction | Notes |
|----------|------------|-----------|-------|
| HLS | http(s):// | In/Out | Apple HTTP Live Streaming, segmented |
| DASH | http(s):// | Out | MPEG-DASH, segmented |
| RTMP | rtmp:// | In/Out | Flash streaming, YouTube/Twitch ingest |
| RTMPS | rtmps:// | In/Out | RTMP over TLS |
| RTSP | rtsp:// | In | IP camera streaming |
| SRT | srt:// | In/Out | Secure Reliable Transport |
| RIST | rist:// | In/Out | Reliable Internet Stream Transport |
| UDP | udp:// | In/Out | Raw UDP multicast/unicast |
| TCP | tcp:// | In/Out | Raw TCP streaming |
| RTP | rtp:// | In/Out | Real-time Transport Protocol |
| pipe | pipe: | In/Out | stdin/stdout piping |

## 3.4 Rate Control

### Quality-Based (Recommended for Storage)

```bash
# CRF (Constant Rate Factor) -- quality-based VBR
ffmpeg -i input.mp4 -c:v libx264 -crf 23 output.mp4           # H.264: 0=lossless, 23=default, 51=worst
ffmpeg -i input.mp4 -c:v libx265 -crf 28 output.mp4           # H.265: 0=lossless, 28=default, 51=worst
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 output.webm  # VP9: 0-63 (must set -b:v 0)
ffmpeg -i input.mp4 -c:v libsvtav1 -crf 35 output.mp4         # SVT-AV1: 0-63
ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -b:v 0 output.mp4 # aom-av1: 0-63

# CQP (Constant Quantizer)
-qp value                                                      # Fixed quantizer parameter

# Lossless
-crf 0        # (libx264, libx265)
-qp 0         # Alternative
```

### Bitrate-Based (Recommended for Streaming)

```bash
# CBR (Constant Bitrate)
ffmpeg -i input.mp4 -c:v libx264 -b:v 5M -maxrate 5M -bufsize 10M output.mp4

# VBR (Variable Bitrate)
ffmpeg -i input.mp4 -c:v libx264 -b:v 5M output.mp4

# ABR (Audio Average Bitrate)
ffmpeg -i input.mp3 -c:a libmp3lame -b:a 192k output.mp3
```

### Multi-Pass Encoding

```bash
ffmpeg -i input.mp4 -c:v libx264 -b:v 5M -pass 1 -f null /dev/null
ffmpeg -i input.mp4 -c:v libx264 -b:v 5M -pass 2 output.mp4
```

### Presets and Tune

```bash
-preset ultrafast|superfast|veryfast|faster|fast|medium|slow|slower|veryslow|placebo
# Slower = better compression at same quality, much slower encode

-tune film         # Live-action content
-tune animation    # Animated content (fewer reference frames)
-tune grain        # Preserve film grain
-tune stillimage   # Still image encoding
-tune psnr         # Optimize for PSNR metric
-tune ssim         # Optimize for SSIM metric
-tune fastdecode   # Reduce decoder complexity
-tune zerolatency  # Real-time streaming (no B-frames, no lookahead)
```

## 3.5 Video Filters (-vf / -filter:v)

Apply with `-vf "filter1=param1=val1:param2=val2,filter2"` or `-filter_complex` for multi-stream.

### Scaling and Geometry

```bash
scale=w:h                                 # Resize (-1 for auto, -2 for auto even)
scale=1920:-1                             # Scale width to 1920, auto height
scale=iw/2:ih/2                           # Half size (iw=input width, ih=input height)
scale=w:h:flags=lanczos                   # With algorithm (bilinear|bicubic|lanczos|spline|...)
scale=w:h:force_original_aspect_ratio=decrease  # Fit within dimensions
zscale=w:h:filter=lanczos                 # HDR-aware scaling (zimg library)

crop=w:h:x:y                              # Crop region
crop=iw:ih-100:0:50                       # Crop 50px top, 50px bottom
crop=in_w:in_w*9/16                       # Crop to 16:9

pad=w:h:x:y:color                         # Add padding / letterbox
pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black   # Center with black bars

rotate=angle*PI/180                        # Rotate by radians
rotate=45*PI/180:fillcolor=none            # 45 degrees with transparent fill
transpose=0                                # 90 CCW + vertical flip
transpose=1                                # 90 CW
transpose=2                                # 90 CCW
transpose=3                                # 90 CW + vertical flip
hflip                                      # Horizontal flip
vflip                                      # Vertical flip

trim=start:end                             # Trim by time (seconds) or frames
trim=start_frame=0:end_frame=100
```

### Text and Overlay

```bash
drawtext=text='Hello':fontsize=48:fontcolor=white:x=10:y=10
drawtext=fontfile=/path/to/font.ttf:text='%{pts\:hms}':fontsize=24:x=10:y=10
# Variables: %{pts} (timestamp), %{pts\:hms} (HH:MM:SS), %{n} (frame number),
#   %{localtime} (clock), %{eif\:n\:d\:6} (frame padded), %{frame_num}
drawtext=textfile=text.txt:reload=1        # Dynamic text from file
drawtext=text='Title':enable='between(t,5,10)'  # Show only between 5-10 seconds

overlay=x:y                                # Overlay image/video
overlay=W-w-10:H-h-10                      # Bottom-right corner (W/H=main, w/h=overlay)
overlay=x:y:enable='between(t,0,5)'       # Timed overlay

subtitles=subs.srt                         # Burn in SRT subtitles
subtitles=subs.srt:force_style='FontSize=24,PrimaryColour=&HFFFFFF'
ass=subs.ass                               # Burn in ASS subtitles
```

### Color Correction

```bash
colorbalance=rs=0.1:gs=0:bs=-0.1:rm=0:gm=0:bm=0:rh=0:gh=0:bh=0
# r/g/b + s(hadows)/m(idtones)/h(ighlights), range -1.0 to 1.0

eq=brightness=0.1:contrast=1.2:saturation=1.5:gamma=1.0
# brightness: -1.0 to 1.0, contrast: 0.0 to 2.0, saturation: 0.0 to 3.0

colorchannelmixer=rr=1:rg=0:rb=0:ra=0:gr=0:gg=1:gb=0:ga=0:br=0:bg=0:bb=1:ba=0
# 4x4 color matrix (12 params for RGB + alpha contribution)

lut=r='val*1.2':g='val':b='val*0.8'       # Per-channel LUT expressions
lut3d=file=lut.cube                        # Apply 3D LUT file (.cube, .3dl)
curves=preset=lighter|darker|increase_contrast|decrease_contrast|negative|cross_process|vintage|...
curves=r='0/0 0.5/0.6 1/1':g='...':b='...'  # Custom spline curves

hue=h=90:s=1                               # Hue shift (degrees) and saturation multiplier

selectivecolor=reds='0 0 0 -0.3':yellows='0 -0.1 0 0'  # CMYK corrections per color range
# Ranges: reds, yellows, greens, cyans, blues, magentas, whites, neutrals, blacks

colorspace=all=bt709                       # Convert color space
tonemap=tonemap_mode                       # HDR to SDR: none|linear|gamma|clip|reinhard|hable|mobius
zscale=transfer=linear:primaries=bt709     # HDR/SDR conversion with zimg
```

### Denoising

```bash
nlmeans=s=3:p=7:r=15                       # Non-local means (s=denoise strength, p=patch, r=research)
hqdn3d=luma_spatial:chroma_spatial:luma_tmp:chroma_tmp  # High-quality 3D denoise
atadenoise=0a=0.02:0b=0.04:1a=0.02:1b=0.04  # Adaptive temporal averaging
bm3d=sigma=10                              # Block-matching 3D (high quality, slow)
fftdnoise=sigma=10                         # FFT-based denoise
vaguedenoiser                              # Wavelet-based denoise
bilateral=sigmaS=0.1:sigmaR=0.1           # Bilateral filter
nlmeans_opencl=s=3:p=7:r=15               # GPU-accelerated NLMeans
```

### Sharpening

```bash
unsharp=5:5:1.0:5:5:0.0                   # luma_msize_x:y:amount:chroma_msize_x:y:amount
cas=strength                               # Contrast Adaptive Sharpening (0.0-1.0)
smartblur=lr=1.0:ls=-0.9:lt=-5            # Smart blur (negative ls = sharpen)
```

### Deinterlacing

```bash
yadif=mode=0:parity=-1:deint=0            # mode: 0=frame, 1=field; parity: 0=tff, 1=bff, -1=auto
bwdif=mode=0                               # Bob Weaver deinterlacing
w3fdif=filter=complex                      # W3FDIF deinterlacing
estdif                                     # Edge slope tracing deinterlace
kerndeint                                  # Kernel-based deinterlace
fieldmatch                                 # Inverse telecine field matching
pullup                                     # Pulldown removal
decimate                                   # Drop duplicate frames after IVTC
```

### Compositing and Keying

```bash
chromakey=color=0x00FF00:similarity=0.15:blend=0.1    # Chroma key (green screen)
colorkey=color=0x00FF00:similarity=0.15:blend=0.1     # Color-based keying
blend=all_mode=overlay:all_opacity=0.5                 # Blend two streams
alphamerge                                             # Merge alpha from second input
alphaextract                                           # Extract alpha channel as grayscale
```

### Stabilization

```bash
# Two-pass stabilization:
vidstabdetect=shakiness=5:accuracy=15:stepsize=6:mincontrast=0.3:result=transforms.trf
vidstabtransform=input=transforms.trf:zoom=1:smoothing=30:interpol=bicubic

deshake=rx=32:ry=32                        # Simpler single-pass stabilization
```

### Timing and Speed

```bash
fps=30                                     # Force output framerate (duplicate/drop frames)
fps=30:round=near                          # round: near|zero|inf|down|up
setpts=0.5*PTS                             # 2x speed (halve timestamps)
setpts=2.0*PTS                             # 0.5x speed (double timestamps)
setpts=PTS-STARTPTS                        # Reset start to zero
framestep=N                                # Output every Nth frame
select='eq(pict_type\,I)'                  # Select only keyframes
select='gte(t,10)*lte(t,20)'              # Select frames between 10-20 seconds
thumbnail=N                                # Select most representative frame per N frames
minterpolate=fps=60:mi_mode=mci           # Motion-interpolated frame rate conversion
```

### Analysis and Detection

```bash
histogram                                  # Display color histogram
waveform                                   # Waveform monitor
vectorscope                                # Color vectorscope
signalstats                                # Video signal statistics
psnr=stats_file=psnr.log                   # PSNR comparison
ssim=stats_file=ssim.log                   # SSIM comparison
vmaf=model_path=/path/to/model             # Netflix VMAF quality metric
scdet=threshold=10                         # Scene change detection (outputs to stderr)
```

## 3.6 Audio Filters (-af / -filter:a)

### Volume and Dynamics

```bash
volume=2.0                                  # Multiply volume (0.0-N, or dB: volume=3dB)
volume=0dB:eval=frame:enable='between(t,0,5)'  # Time-based volume

loudnorm=I=-16:LR=-1:TP=-1.5              # EBU R128 loudness normalization
# I=integrated loudness (LUFS), LR=loudness range, TP=true peak (dBTP)
# Two-pass for best results:
#   Pass 1: ffmpeg -i in.wav -af loudnorm=print_format=json -f null /dev/null
#   Pass 2: ffmpeg -i in.wav -af loudnorm=...:measured_I=...:measured_LRA=...:measured_TP=...:measured_thresh=... out.wav

dynaudnorm=framelen=500:gausssize=31       # Dynamic audio normalization (per-window)
compand=attacks=0:decays=0.1:points=-80/-80|-12/-12|0/-6|20/-3  # Compand (compress/expand)
acompressor=threshold=-20dB:ratio=4:attack=5:release=50:makeup=2  # Dynamic range compressor
alimiter=limit=0.95:level=enabled          # Hard limiter
agate=threshold=-40dB:ratio=4:attack=1:release=100  # Noise gate
sidechaingate                              # Sidechain-triggered noise gate
```

### Equalization

```bash
equalizer=f=1000:t=h:w=200:g=5            # Parametric EQ (f=freq, t=h/q/o/s, w=width, g=gain dB)
bass=g=5:f=100:t=h:w=200                  # Bass boost/cut
treble=g=3:f=8000:t=h:w=200               # Treble boost/cut
bandpass=f=1000:t=h:w=200                  # Bandpass filter
bandreject=f=1000:t=h:w=200               # Band-reject (notch) filter
highpass=f=200:p=2                         # Highpass filter (p=poles/order)
lowpass=f=8000:p=2                         # Lowpass filter
allpass=f=1000:t=h:w=200                   # Allpass filter (phase shift)
biquad=b0=1:b1=0:b2=0:a0=1:a1=0:a2=0     # Generic biquad filter
firequalizer=gain='if(lt(f,1000),0,-INF)' # FIR equalizer with expression
superequalizer=1b=0:2b=0:...               # 18-band graphic equalizer
```

### Effects

```bash
aecho=0.8:0.88:60:0.4                     # in_gain:out_gain:delays_ms:decays
chorus=0.5:0.9:50|60|40:0.4|0.32|0.3:0.25|0.4|0.3:2|2.3|1.3  # Chorus effect
flanger=delay=0:depth=2:speed=0.5:regen=0:width=71:shape=sin:phase=25
phaser=in_gain=0.4:out_gain=0.74:delay=3:speed=0.4:type=triangular
tremolo=f=5:d=0.5                          # f=frequency Hz, d=depth 0.0-1.0
vibrato=f=5:d=0.5                          # Pitch vibrato
crystalizer=i=2                            # Expand audio dynamic range
haas                                       # Haas stereo effect
stereotools=mlev=1:slev=1:balance_in=0:...  # Stereo manipulation
stereowiden=delay=20:feedback=0.3:crossfeed=0.3:drymix=0.8
extrastereo=m=2.5                          # Exaggerate stereo separation
```

### Channel Manipulation

```bash
pan=stereo|c0=c0+0.5*c1|c1=0.5*c0+c1     # Channel mixing/panning
pan=mono|c0=0.5*c0+0.5*c1                 # Downmix to mono
channelmap=map=0-0|1-1                     # Remap channels
channelsplit                               # Split to individual mono streams
amerge=inputs=2                            # Merge mono streams to multi-channel
amix=inputs=2:duration=longest:dropout_transition=3  # Mix multiple inputs
join=inputs=2:channel_layout=stereo        # Join streams into multi-channel
aresample=48000                            # Resample to target sample rate
aformat=sample_fmts=s16:sample_rates=44100:channel_layouts=stereo  # Force format
```

### Timing and Selection

```bash
atempo=2.0                                 # Audio speed 0.5-100.0 (chain for extremes: atempo=2.0,atempo=2.0 = 4x)
asetpts=N/SR/TB                            # Reset audio timestamps
aloop=loop=0:size=44100:start=0            # Loop audio (0=infinite)
atrim=start=5:end=30                       # Trim by seconds
aselect='between(t,5,10)'                 # Select audio by expression
apad=whole_len=441000                      # Pad with silence to length
apad=pad_dur=2                             # Pad with N seconds silence
```

### Silence Detection and Removal

```bash
silencedetect=noise=-50dB:d=0.5            # Detect silence (outputs to stderr)
# d=minimum duration, noise=threshold
silenceremove=start_periods=1:start_silence=0.5:start_threshold=-50dB:stop_periods=1:stop_silence=0.5:stop_threshold=-50dB
```

### Noise Reduction

```bash
anlmdn=s=7:p=0.002:r=0.002:m=15           # Audio non-local means denoise
afftdn=nr=20:nf=-30                        # FFT-based noise reduction (nr=reduction dB, nf=floor dB)
arnndn=model=/path/to/model.rnnn           # RNN-based noise suppression (AI-powered)
```

### Analysis

```bash
astats=metadata=1:reset=1                  # Audio statistics (per-frame or whole)
# Output: DC_offset, Min_level, Max_level, Peak_level, RMS_level, Crest_factor, etc.
ameter                                     # Audio level meter
ebur128=peak=true                          # EBU R128 loudness meter
showspectrum=s=1280x720                    # Spectrum visualization
showwaves=s=1280x720:mode=cline           # Waveform visualization (line|point|cline|p2p)
showcqt=s=1920x1080                        # Constant-Q transform visualization
```

## 3.7 Device Capture

### Windows

```bash
# Screen capture
ffmpeg -f gdigrab -framerate 30 -i desktop output.mp4
ffmpeg -f gdigrab -framerate 30 -offset_x 100 -offset_y 200 -video_size 1280x720 -i desktop output.mp4
ffmpeg -f gdigrab -framerate 30 -i title="Window Title" output.mp4

# Webcam and microphone
ffmpeg -f dshow -i video="Camera Name" output.mp4
ffmpeg -f dshow -i audio="Microphone Name" output.wav
ffmpeg -f dshow -i video="Camera Name":audio="Microphone Name" output.mp4

# List devices
ffmpeg -f dshow -list_devices true -i dummy
```

### Linux

```bash
# Screen capture
ffmpeg -f x11grab -framerate 30 -video_size 1920x1080 -i :0.0+0,0 output.mp4

# Webcam
ffmpeg -f v4l2 -framerate 30 -video_size 1280x720 -i /dev/video0 output.mp4

# Audio
ffmpeg -f alsa -i default output.wav
ffmpeg -f pulse -i default output.wav
```

### macOS

```bash
# Screen + audio
ffmpeg -f avfoundation -framerate 30 -i "1:0" output.mp4
# Device indices: ffmpeg -f avfoundation -list_devices true -i ""
```

## 3.8 Subtitles

### Supported Formats

| Format | Extension | Type | Read | Write |
|--------|-----------|------|------|-------|
| SubRip | .srt | Text | Y | Y |
| ASS/SSA | .ass/.ssa | Text (styled) | Y | Y |
| WebVTT | .vtt | Text | Y | Y |
| PGS/SUP | .sup | Bitmap | Y | Y |
| DVB | embedded | Bitmap | Y | Y |
| MOV_TEXT | embedded (.mp4) | Text | Y | Y |
| XSUB | embedded | Bitmap | Y | N |
| EIA-608 | embedded | Text | Y | Y |
| EIA-708 | embedded | Text | Y | N |

### Operations

```bash
# Burn subtitles into video (hardcode)
ffmpeg -i video.mp4 -vf subtitles=subs.srt output.mp4
ffmpeg -i video.mp4 -vf ass=subs.ass output.mp4
ffmpeg -i video.mp4 -vf subtitles=subs.srt:force_style='FontSize=24' output.mp4

# Extract subtitles
ffmpeg -i video.mkv -map 0:s:0 output.srt           # First subtitle track
ffmpeg -i video.mkv -map 0:s:1 output.ass           # Second subtitle track

# Convert between formats
ffmpeg -i subs.srt subs.ass
ffmpeg -i subs.ass subs.vtt

# Embed subtitles as soft subs
ffmpeg -i video.mp4 -i subs.srt -c copy -c:s mov_text output.mp4       # MP4
ffmpeg -i video.mp4 -i subs.srt -c copy -c:s srt output.mkv            # MKV
ffmpeg -i video.mp4 -i subs.ass -c copy -c:s ass output.mkv

# Multiple subtitle tracks
ffmpeg -i video.mp4 -i english.srt -i french.srt \
  -map 0:v -map 0:a -map 1 -map 2 \
  -metadata:s:s:0 language=eng -metadata:s:s:1 language=fre \
  -c:s srt output.mkv
```

## 3.9 Image Operations

```bash
# Single image input
ffmpeg -i image.png -vf scale=800:-1 resized.png

# Image sequence to video
ffmpeg -framerate 30 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# Video to image sequence
ffmpeg -i video.mp4 frame_%04d.png

# Extract single frame
ffmpeg -i video.mp4 -ss 00:01:30 -frames:v 1 frame.png

# Smart thumbnail extraction
ffmpeg -i video.mp4 -vf thumbnail=300 -frames:v 1 thumb.png   # Best frame per 300

# GIF with palette optimization
ffmpeg -i video.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,palettegen" palette.png
ffmpeg -i video.mp4 -i palette.png -filter_complex "fps=15,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse" output.gif

# Animated WebP
ffmpeg -i video.mp4 -vf "fps=15,scale=480:-1" -loop 0 output.webp
```

## 3.10 Advanced Features

### Complex Filtergraphs

`-filter_complex` for multi-stream graphs. Syntax: label each link `[name]`; chain filters with `;`; reference labels by name. Example shape:

```
[0:v]scale=1920:1080[scaled]; [scaled][1:v]overlay=W-w-10:10[out]
```

See the "complex filtergraph" escape-hatch recipe below for a realistic PIP example.

### Concatenation

```bash
# Concat demuxer (same codec, recommended)
# files.txt:
#   file 'part1.mp4'
#   file 'part2.mp4'
ffmpeg -f concat -safe 0 -i files.txt -c copy output.mp4

# Concat filter (re-encode, different formats OK)
ffmpeg -i part1.mp4 -i part2.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" output.mp4

# Concat protocol (MPEG-TS only)
ffmpeg -i "concat:part1.ts|part2.ts" -c copy output.ts
```

### Stream Selection (-map)

```bash
-map 0              # All streams from input 0
-map 0:v            # All video streams from input 0
-map 0:a            # All audio streams from input 0
-map 0:s            # All subtitle streams from input 0
-map 0:v:0          # First video stream from input 0
-map 0:a:1          # Second audio stream from input 0
-map -0:a:1         # Exclude second audio stream from input 0
-map 0:m:language:eng  # Streams with English language metadata
```

### Seeking and Trimming

```bash
-ss HH:MM:SS.ms     # Seek to position (before -i = input seek, after -i = output seek)
-to HH:MM:SS.ms     # Stop at position
-t duration          # Duration in seconds
-sseof -10           # Seek to 10 seconds before end

# Fast seek (before input) + precise cut (after input)
ffmpeg -ss 00:01:00 -i input.mp4 -to 00:00:30 -c copy output.mp4

# Frame-accurate cut (re-encode)
ffmpeg -ss 00:01:00 -i input.mp4 -t 30 -c:v libx264 -c:a aac output.mp4
```

### Speed Changes

```bash
# Video speed (setpts)
-vf setpts=0.5*PTS                  # 2x speed
-vf setpts=2.0*PTS                  # 0.5x speed
-vf setpts=PTS/1.5                  # 1.5x speed

# Audio speed (atempo), chainable for values outside 0.5-2.0
-af atempo=2.0                      # 2x speed
-af atempo=0.5                      # 0.5x speed
-af atempo=2.0,atempo=2.0           # 4x speed (chained)

# Combined audio+video speed change
ffmpeg -i input.mp4 -vf setpts=0.5*PTS -af atempo=2.0 output.mp4
```

### Metadata and Chapters

```bash
-metadata title="My Video"
-metadata:s:v:0 title="Video Track"
-metadata:s:a:0 language=eng
-metadata:s:a:1 language=fra
-disposition:a:0 default                # Set default audio track
-disposition:s:0 0                      # Remove default subtitle flag
-map_metadata 0                         # Copy metadata from input 0
-map_chapters 0                         # Copy chapters from input 0
```

### Miscellaneous

```bash
-shortest                               # End output when shortest input ends
-stream_loop N                          # Loop input N times (-1=infinite)
-f segment -segment_time 10             # Segment output into 10-second chunks
-f tee "[f=mp4]out.mp4|[f=flv]rtmp://..." # Output to multiple destinations
-err_detect explode                     # Strict error handling
-max_muxing_queue_size 1024             # Increase mux queue (fix interleaving errors)
-movflags +faststart                    # Move moov atom for web streaming (MP4)
-threads N                              # Thread count (0=auto)
-loglevel quiet|error|warning|info|verbose|debug
-y                                      # Overwrite output without asking
-n                                      # Never overwrite output
-progress url                           # Send encoding progress to URL/pipe
-vstats_file file                       # Write encoding stats
```

### Reverse

```bash
ffmpeg -i input.mp4 -vf reverse -af areverse output.mp4      # Reverse (entire file in memory)
# For large files, split first, reverse segments, then concat
```

### Pipe I/O

```bash
ffmpeg -i pipe:0 -f mp4 pipe:1          # Read from stdin, write to stdout
cat input.raw | ffmpeg -f rawvideo -pix_fmt rgb24 -s 1920x1080 -i - output.mp4
ffmpeg -i input.mp4 -f rawvideo -pix_fmt rgb24 - | python process.py
```

## 3.11 ffprobe

```bash
ffprobe [options] input_file
```

### Output Formats

```bash
-of default                # Human-readable (default)
-of compact                # Compact single-line
-of csv                    # Comma-separated
-of flat                   # Flat key=value
-of ini                    # INI-style
-of json                   # JSON (most useful for programmatic access)
-of xml                    # XML
```

### Show Sections

```bash
-show_format               # Container format info (duration, bitrate, tags)
-show_streams              # Stream info (codec, resolution, sample rate, etc.)
-show_frames               # Per-frame info (type, size, timestamp)
-show_packets              # Per-packet info
-show_chapters             # Chapter markers
-show_programs             # Program info (multi-program transport streams)
-show_entries section=key1,key2  # Select specific fields
```

### Common Queries

```bash
# Full info as JSON
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Duration only
ffprobe -v quiet -show_entries format=duration -of csv=p=0 input.mp4

# Video resolution
ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 input.mp4

# Audio sample rate and channels
ffprobe -v quiet -select_streams a:0 -show_entries stream=sample_rate,channels -of csv=p=0 input.mp4

# Codec names
ffprobe -v quiet -show_entries stream=codec_name -of csv=p=0 input.mp4

# Bitrate
ffprobe -v quiet -show_entries format=bit_rate -of csv=p=0 input.mp4

# Frame count
ffprobe -v quiet -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 input.mp4
```

---

# Quick Cross-Reference

| Task | Pillow | ImageMagick | FFmpeg |
|------|--------|-------------|--------|
| Resize image | `img.resize((w,h))` | `magick in -resize WxH out` | `ffmpeg -i in -vf scale=W:H out` |
| Crop | `img.crop((l,t,r,b))` | `magick in -crop WxH+X+Y out` | `ffmpeg -i in -vf crop=W:H:X:Y out` |
| Rotate | `img.rotate(angle)` | `magick in -rotate angle out` | `ffmpeg -i in -vf rotate=a out` |
| Blur | `img.filter(GaussianBlur(r))` | `magick in -blur 0xS out` | `ffmpeg -i in -vf gblur=sigma=S out` |
| Add text | `draw.text(xy, text)` | `magick in -annotate +X+Y "text" out` | `ffmpeg -i in -vf drawtext=text='t' out` |
| Grayscale | `img.convert("L")` | `magick in -colorspace Gray out` | `ffmpeg -i in -vf format=gray out` |
| Format convert | `img.save("out.jpg")` | `magick in.png out.jpg` | `ffmpeg -i in.png out.jpg` |
| Overlay | `img.paste(overlay, pos)` | `magick base overlay -composite out` | `-filter_complex overlay=X:Y` |
| Brightness | `ImageEnhance.Brightness(img)` | `magick in -brightness-contrast B out` | `-vf eq=brightness=B` |
| Thumbnail | `img.thumbnail((w,h))` | `magick in -thumbnail WxH out` | `-vf thumbnail=N -frames:v 1` |

---

## Escape-hatch recipes

These are flows `claw` explicitly doesn't wrap — use the library / raw CLI directly.

### 1. Pillow channel math — isolate red, cancel green

`ImageChops` + `split()` + `merge()` is how you do per-channel arithmetic. No flag surface wraps this:

```python
from PIL import Image, ImageChops
r, g, b = Image.open("in.png").split()
r = ImageChops.add(r, ImageChops.constant(r, 40))     # +40 red
g = ImageChops.multiply(g, ImageChops.constant(g, 0))  # zero green
Image.merge("RGB", (r, g, b)).save("out.png")
```

### 2. ImageMagick morphology — seam-thin then prune

Custom kernel chains are why `magick` exists. `claw` won't try to flagify this:

```bash
magick in.png -threshold 50% \
  -morphology Thinning:-1 Skeleton \
  -morphology Pruning:-1 1 \
  skeleton.png
```

### 3. Complex ffmpeg filtergraph — picture-in-picture with fade

Multi-input + split + overlay + fade all in one `-filter_complex` — `claw media` covers compress/scale/trim but not this shape:

```bash
ffmpeg -i main.mp4 -i webcam.mp4 -filter_complex "
  [1:v]scale=320:180,setpts=PTS-STARTPTS[pip];
  [0:v][pip]overlay=W-w-20:H-h-20:enable='between(t,2,60)'[v];
  [v]fade=in:0:30,fade=out:st=58:d=2[vfaded]
" -map "[vfaded]" -map 0:a -c:v libx264 -crf 20 out.mp4
```

### 4. Two-pass EBU R128 loudness normalization

The single-pass approximation is what `claw media loudnorm` emits. For broadcast-grade output you need two passes to feed measured values in:

```bash
# pass 1 — measure
ffmpeg -i in.wav -af loudnorm=I=-16:LRA=7:TP=-1.5:print_format=json -f null - 2>meta.log
# pull measured_I / measured_LRA / measured_TP / measured_thresh from meta.log
# pass 2 — apply
ffmpeg -i in.wav -af "loudnorm=I=-16:LRA=7:TP=-1.5:measured_I=-22.31:measured_LRA=10.8:measured_TP=-4.2:measured_thresh=-32.65:linear=true" out.wav
```

### 5. Device capture on Windows (gdigrab + dshow)

`claw` doesn't spawn capture pipelines — they're long-running and OS-specific:

```bash
ffmpeg -f gdigrab -framerate 30 -i desktop \
       -f dshow -i audio="Microphone (USB Mic)" \
       -c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 160k \
       screencast.mkv
```

### 6. HDR → SDR tone-map with zscale + tonemap

Proper HDR downconversion needs the zimg filter chain, not a preset:

```bash
ffmpeg -i hdr.mp4 -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" -c:v libx264 -crf 20 sdr.mp4
```
