# `claw media` — Video / Audio Operations Reference

CLI wrapper over `ffmpeg` and `ffprobe` for multimedia processing. Handles metadata extraction, transcoding, and editing.

## Contents

- **INSPECT**
  - [Stream Info](#11-info)
- **EXTRACT**
  - [Extract Audio](#21-extract-audio) · [Generate Thumbnail](#22-thumbnail)
- **TRANSFORM**
  - [Trim](#31-trim) · [Compress](#32-compress) · [Scale](#33-scale) · [Change Speed](#34-speed) · [Fade In/Out](#35-fade) · [Burn Subtitles](#36-burn-subs) · [Concat](#37-concat) · [Auto Crop](#38-crop-auto) · [Loudness Norm](#39-loudnorm) · [To GIF](#310-gif)

---

## Critical Rules

1. **FFmpeg Dependency** — All `media` commands require `ffmpeg` and `ffprobe` to be installed and available in the system PATH.
2. **Re-encoding** — Most transformation commands (trim, scale, etc.) perform re-encoding by default to ensure accuracy, which can be CPU intensive.
3. **Codec Support** — Support for specific codecs (H.264, H.265, VP9) depends on the version of FFmpeg installed on the host.
4. **Fast Seek** — Use `--from` before the input filename (if supported by the specific subcommand) for faster seeking on large files.

---

## 1.1 info
Display detailed stream information (codecs, bitrate, resolution) via `ffprobe`.
```bash
claw media info <SRC> [--json]
```

---

## 2.1 extract-audio
Rip audio tracks from a video file.
```bash
claw media extract-audio <SRC> --out <OUT> [--format mp3|wav|m4a] [--bitrate 192k] [--force]
```

## 2.2 thumbnail
Extract a single frame or create a contact sheet.
```bash
claw media thumbnail <SRC> --out <OUT> --at <SECONDS|HH:MM:SS> [--scale WxH] [--force]
```

---

## 3.1 trim
Cut a segment from a media file.
```bash
claw media trim <SRC> --out <OUT> --from <T> [--to <T>|--duration <T>] [--force]
```

## 3.2 compress
Reduce file size by adjusting bitrate or using CRF (Constant Rate Factor).
```bash
claw media compress <SRC> --out <OUT> [--target-size MB] [--crf N] [--force]
```

## 3.3 scale
Change video resolution.
```bash
claw media scale <SRC> --size <WxH> --out <OUT> [--preserve-aspect] [--force]
```

## 3.4 speed
Speed up or slow down media (adjusts both video and audio).
```bash
claw media speed <SRC> --factor <FLOAT> --out <OUT> [--force]
```

## 3.5 fade
Add fade-in or fade-out transitions.
```bash
claw media fade <SRC> --type <in|out|both> --duration <SECONDS> --out <OUT> [--force]
```

## 3.6 burn-subs
Hard-code subtitles into the video stream.
```bash
claw media burn-subs <SRC> --subs <FILE.srt|.ass> --out <OUT> [--force]
```

## 3.7 concat
Stitch multiple media files together.
```bash
claw media concat <INPUTS...> --out <OUT> [--safe] [--force]
```

## 3.8 crop-auto
Detect and remove black bars (letterboxing).
```bash
claw media crop-auto <SRC> --out <OUT> [--force]
```

## 3.9 loudnorm
Normalize audio loudness to EBU R128 standards.
```bash
claw media loudnorm <SRC> --out <OUT> [--target <DBLU>] [--force]
```

## 3.10 gif
Convert a video clip into an animated GIF.
```bash
claw media gif <SRC> --out <OUT_GIF> [--fps 15] [--scale 480] [--force]
```

---

## Footguns
- **Variable Frame Rate** — Fast-seeking (`--from`) on VFR video can sometimes lead to slightly inaccurate cut points.
- **Concat Mismatch** — `concat` will fail or produce glitchy output if input files have different resolutions or timebases; use a filter-based approach for mismatched files.

## Escape Hatch
Underlying tool: `ffmpeg`. For complex filtergraphs, use `run_shell_command` to execute `ffmpeg` directly.

## Quick Reference
| Task | Command |
|------|---------|
| Stream Info | `claw media info video.mp4` |
| Extract MP3 | `claw media extract-audio video.mp4 --out audio.mp3` |
| Take Snapshot | `claw media thumbnail video.mp4 --at 00:05:00` |
| Compress File | `claw media compress video.mp4 --target-size 10MB` |
| Clip Video | `claw media trim video.mp4 --from 10 --to 20` |
