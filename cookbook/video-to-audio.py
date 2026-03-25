#!/usr/bin/env python3
"""
Cortex Example: video-to-audio
Description: Extract audio from video files with batch support
Tags: ffmpeg,video,audio,extraction
Captured: 2026-03-25
Source: video-to-audio.py

Usage:
  python ~/.claude/skills/cortex/cookbook/video-to-audio.py
"""

#!/usr/bin/env python3
"""
Extract audio from video files using ffmpeg. Supports batch processing.
Output format: MP3, WAV, AAC, or FLAC.

Usage:
    python video-to-audio.py input.mp4 [output.mp3]
    python video-to-audio.py input_dir/ output_dir/ --format wav --bitrate 192k
"""

import sys
import argparse
import subprocess
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv"}


def extract_audio(input_path, output_path, fmt="mp3", bitrate="128k"):
    cmd = [
        "ffmpeg", "-i", str(input_path),
        "-vn",  # no video
        "-acodec", {"mp3": "libmp3lame", "wav": "pcm_s16le", "aac": "aac", "flac": "flac"}[fmt],
        "-ab", bitrate,
        "-y",  # overwrite
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {input_path.name}: {result.stderr[-200:]}")
        return False
    print(f"  {input_path.name} → {output_path.name}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Extract audio from video files")
    parser.add_argument("input", help="Input video file or directory")
    parser.add_argument("output", nargs="?", help="Output file or directory")
    parser.add_argument("--format", choices=["mp3", "wav", "aac", "flac"], default="mp3")
    parser.add_argument("--bitrate", default="128k")
    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file():
        output = Path(args.output) if args.output else input_path.with_suffix(f".{args.format}")
        extract_audio(input_path, output, args.format, args.bitrate)
    elif input_path.is_dir():
        output_dir = Path(args.output) if args.output else input_path / "audio"
        output_dir.mkdir(parents=True, exist_ok=True)
        videos = [f for f in input_path.iterdir() if f.suffix.lower() in VIDEO_EXTS]
        print(f"Processing {len(videos)} videos...")
        for v in sorted(videos):
            out = output_dir / f"{v.stem}.{args.format}"
            extract_audio(v, out, args.format, args.bitrate)
        print(f"\nDone → {output_dir}")
    else:
        print(f"Error: {input_path} not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
