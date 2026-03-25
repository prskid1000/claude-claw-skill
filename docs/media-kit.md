# Media Kit — Image, Video, Audio & Conversion

> FFmpeg, Pillow, ImageMagick, Pandoc, and screenshot tools.

**Related:** [doc-forge.md](doc-forge.md) | [pipelines.md](pipelines.md)

---

## Screenshots

| Source | Method |
|--------|--------|
| PDF page | `fitz` (pymupdf) — see below |
| Web page | Chrome DevTools MCP skill → `navigate_page` → `screenshot` (uses Edge) |
| Document | Convert to PDF first (`pandoc X.docx -o X.pdf`) then screenshot with fitz |

```python
import fitz
doc = fitz.open("file.pdf")
pix = doc[0].get_pixmap(matrix=fitz.Matrix(3, 3))  # 3x for high-res
pix.save("screenshot.png")
```

## Pillow — Image Manipulation

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

img = Image.open("input.png")

# Resize / thumbnail
img = img.resize((800, 600), Image.LANCZOS)
img.thumbnail((300, 300))  # preserves aspect ratio

# Crop
img = img.crop((left, top, right, bottom))

# Text overlay
draw = ImageDraw.Draw(img)
font = ImageFont.load_default(size=36)
draw.text((50, 50), "Watermark", fill=(255, 0, 0), font=font)

# Format conversion
img.save("out.jpg", "JPEG", quality=85)
img.save("out.webp", "WEBP", quality=80)

# Composite
bg = Image.open("bg.png")
overlay = Image.open("logo.png").resize((100, 100))
bg.paste(overlay, (10, 10), overlay)

# Filters & enhance
img = img.filter(ImageFilter.SHARPEN)
img = ImageEnhance.Brightness(img).enhance(1.5)
img = ImageEnhance.Contrast(img).enhance(1.3)

# Create blank diagram
img = Image.new('RGB', (800, 600), 'white')
draw = ImageDraw.Draw(img)
draw.rectangle([50, 50, 750, 550], outline='black', width=2)
draw.line([(100, 500), (200, 300), (400, 200)], fill='blue', width=3)
img.save("diagram.png")
```

## ImageMagick — CLI

```bash
magick input.png -resize 800x600 output.png          # Resize
magick input.png output.jpg                           # Convert format
magick input.png -border 10 -bordercolor "#333" o.png # Border
magick input.png -pointsize 36 -fill red -annotate +50+50 "Text" o.png  # Annotate
magick bg.png logo.png -gravity southeast -composite o.png  # Overlay
magick mogrify -format jpg -quality 85 *.png          # Batch convert
magick montage a.png b.png c.png -geometry 300x200+5+5 grid.png  # Grid
magick -density 300 input.pdf output_%03d.png         # PDF → images
magick input.png -trim +repage output.png             # Trim whitespace
magick input.png -rotate 90 output.png                # Rotate
```

## FFmpeg — Audio & Video

```bash
# --- Convert ---
ffmpeg -i input.mp4 -c:v libx264 -crf 23 output.mp4
ffmpeg -i input.mkv -c:v copy -c:a copy output.mp4   # Remux (fast)

# --- Extract audio ---
ffmpeg -i input.mp4 -vn -acodec mp3 -ab 192k output.mp3
ffmpeg -i input.mp4 -vn -acodec pcm_s16le output.wav

# --- Trim ---
ffmpeg -i input.mp4 -ss 00:01:00 -t 00:00:30 -c copy clip.mp4
ffmpeg -i input.mp4 -ss 00:05:00 -to 00:10:00 -c copy segment.mp4

# --- Merge ---
# list.txt: file 'clip1.mp4'\nfile 'clip2.mp4'
ffmpeg -f concat -safe 0 -i list.txt -c copy merged.mp4

# --- Thumbnails ---
ffmpeg -i input.mp4 -vf "thumbnail" -frames:v 1 thumb.jpg
ffmpeg -i input.mp4 -ss 00:00:05 -frames:v 1 frame.png
ffmpeg -i input.mp4 -vf "fps=1" frames/frame_%04d.png

# --- Compress / resize ---
ffmpeg -i input.mp4 -vcodec libx264 -crf 28 -preset fast compressed.mp4
ffmpeg -i input.mp4 -vf scale=1280:720 resized.mp4

# --- Add subtitles / audio ---
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output.mp4
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest output.mp4

# --- GIF ---
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos" output.gif

# --- Speed ---
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -filter:a "atempo=2.0" fast.mp4

# --- Audio convert ---
ffmpeg -i input.wav -acodec mp3 -ab 320k output.mp3

# --- Media info ---
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# --- Screen record (Windows) ---
ffmpeg -f gdigrab -framerate 30 -video_size 1920x1080 -i desktop output.mp4
```

## Pandoc — Document Conversion

```bash
pandoc input.md -o output.docx                        # Markdown → Word
pandoc input.md -o output.pdf --pdf-engine=xelatex    # Markdown → PDF
pandoc input.md -o output.pdf --toc --toc-depth=3     # With TOC
pandoc input.docx -o output.md                        # Word → Markdown
pandoc input.docx -o output.pdf                       # Word → PDF
pandoc input.html -o output.docx                      # HTML → Word
pandoc input.md -o output.pptx                        # Markdown → PPT
pandoc input.md -o output.html --standalone --css=s.css  # Styled HTML
pandoc input.md -o out.docx --reference-doc=tmpl.docx # With template
pandoc ch1.md ch2.md -o book.docx                     # Multi-input
pandoc input.md -o out.pdf --metadata title="T" --metadata author="A"
```

**Note:** PDF output via pandoc requires LaTeX (`xelatex`). If not installed, use pymupdf/reportlab instead — see [doc-forge.md](doc-forge.md).
