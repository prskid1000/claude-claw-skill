# `claw media` — Video / Audio Reference

CLI wrapper over ffmpeg / ffprobe.

## Contents
- [Info](#info) · [Extract](#extract) · [Transform](#transform)

---

## Info
### `info`
```bash
claw media info <SRC> [--json]
```

## Extract
### `extract-audio`
```bash
claw media extract-audio <SRC> --out <OUT> [--format mp3|wav|...] [--force]
```
### `thumbnail`
```bash
claw media thumbnail <SRC> --out <OUT> --at <SECONDS|HH:MM:SS> [--force]
```

## Transform
### `trim`
```bash
claw media trim <SRC> --out <OUT> --from <T> --to <T> [--force]
```
### `compress`
```bash
claw media compress <SRC> --out <OUT> [--target-size MB] [--crf N] [--force]
```

---

## Quick Reference
| Task | Command |
|------|---------|
| Metadata | `claw media info f.mp4` |
| Thumb | `claw media thumbnail f.mp4 --at 10 --out t.jpg` |
| Trim | `claw media trim f.mp4 --out t.mp4 --from 0 --to 60` |
