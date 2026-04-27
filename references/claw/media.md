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
Rip an audio track from a video file. `--quality` is a codec-native quality knob (not a bitrate string). Use `--track` to pick a specific audio stream index.
```bash
claw media extract-audio <SRC> --out <OUT> [--format mp3|aac|wav|opus|flac] [--quality <INT>] [--track <INT>]
```

## 2.2 thumbnail
Grab a single frame at `--at`, OR build a contact sheet with `--count` + `--grid`. `--width` sets per-frame width (height auto).
```bash
claw media thumbnail <SRC> --out <OUT> [--at <SEC|HH:MM:SS>] [--count <N>] [--grid <WxH>] [--width <PX>]
```

---

## 3.1 trim
Cut a segment from a media file.
```bash
claw media trim <SRC> --out <OUT> --from <T> [--to <T>|--duration <T>] [--force]
```

## 3.2 compress
Shrink video to `--target-size` (2-pass) OR `--crf` (1-pass). Pick a codec via `--codec`; tune speed/quality tradeoff via `--preset`.
```bash
claw media compress <SRC> --out <OUT> [--target-size 25M|1.5G] [--crf <INT>] [--codec h264|h265|vp9|av1] [--preset <NAME>] [--audio-bitrate <RATE>]
```

## 3.3 scale
Scale a video to a target geometry (ImageMagick geometry syntax, e.g. `1280x720`, `1280x`, `50%`).
```bash
claw media scale <SRC> --geometry <GEOM> --out <OUT> [--codec h264|h265|vp9|av1] [--crf <INT>]
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
Convert a video slice into an animated GIF. `--duration` is required; `--start` sets the slice origin. Sizing is via `--width` (not a `WxH` scale).
```bash
claw media gif <SRC> --out <OUT_GIF> --duration <SEC> [--start <SEC|HH:MM:SS>] [--width <PX>] [--fps <INT>] [--dither bayer|sierra|none]
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
