"""LM Studio white tray-icon patcher — single-file apply / restore / status.

LM Studio's tray icon on Windows is a single hardcoded file
(C:\\Program Files\\LM Studio\\resources\\icon.ico) — `trayIconPath()`
in its obfuscated main bundle returns `path.join(process.resourcesPath,
'icon.ico')` on win32, ignoring state and theme.

This script replaces icon.ico with a white-bars silhouette rendered
in-memory from the BARS_64 constant below. Edit BARS_64 to tweak the
design; next `apply` pushes the new rendering. Re-run `apply` after
any LM Studio update — the updater overwrites icon.ico.

Usage:
    python lm-studio-white-tray.py apply     # replace icon.ico (UAC)
    python lm-studio-white-tray.py restore   # revert to original (UAC)
    python lm-studio-white-tray.py status    # show current state

Exit codes:
    0 = success (or nothing to do)
    1 = handled error
    2 = LM Studio not installed
"""

from __future__ import annotations

import ctypes
import hashlib
import io
import shutil
import struct
import sys
import tempfile
import zlib
from pathlib import Path


LM_STUDIO_RESOURCES = Path(r'C:\Program Files\LM Studio\resources')
ICON_TARGET = LM_STUDIO_RESOURCES / 'icon.ico'
ICON_BACKUP = LM_STUDIO_RESOURCES / 'icon.original.ico'

ICO_SIZES = [16, 20, 24, 32, 40, 48, 64, 128, 256]

# (y_center, x_start, x_end, thickness) in a 64x64 grid. Rounded caps automatic.
BARS_64 = [
    (15, 14, 40, 4),
    (23, 30, 50, 4),
    (31, 14, 50, 5),
    (40, 24, 50, 4),
    (48, 14, 38, 4),
]


def _in_bar(fx: float, fy: float, bar: tuple[int, int, int, int]) -> bool:
    cy, x0, x1, th = bar
    r = th / 2.0
    if fy < cy - r or fy > cy + r:
        return False
    if x0 + r <= fx <= x1 - r:
        return True
    dx0 = fx - (x0 + r)
    dy = fy - cy
    if dx0 < 0 and dx0 * dx0 + dy * dy <= r * r:
        return True
    dx1 = fx - (x1 - r)
    if dx1 > 0 and dx1 * dx1 + dy * dy <= r * r:
        return True
    return False


def _png_chunk(ct: bytes, data: bytes) -> bytes:
    c = ct + data
    return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)


def _render_png(size: int) -> bytes:
    S = size / 64.0
    TRANSPARENT = bytes([0, 0, 0, 0])
    WHITE = bytes([255, 255, 255, 255])
    raw = bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):
            fx = x / S
            fy = y / S
            hit = any(_in_bar(fx, fy, b) for b in BARS_64)
            raw += WHITE if hit else TRANSPARENT
    buf = io.BytesIO()
    buf.write(b'\x89PNG\r\n\x1a\n')
    buf.write(_png_chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)))
    buf.write(_png_chunk(b'IDAT', zlib.compress(bytes(raw), 9)))
    buf.write(_png_chunk(b'IEND', b''))
    return buf.getvalue()


def render_ico() -> bytes:
    pngs = [(s, _render_png(s)) for s in ICO_SIZES]
    out = io.BytesIO()
    out.write(struct.pack('<HHH', 0, 1, len(pngs)))
    entry_offset = 6 + 16 * len(pngs)
    for s, png in pngs:
        w = s if s < 256 else 0
        h = s if s < 256 else 0
        out.write(struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(png), entry_offset))
        entry_offset += len(png)
    for _, png in pngs:
        out.write(png)
    return out.getvalue()


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def require_admin(command: str) -> None:
    if is_admin():
        return
    print(f'[INFO] elevation required for "{command}" - re-launching with UAC')
    params = ' '.join(f'"{a}"' for a in [str(Path(__file__).resolve()), command])
    ret = ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, params, None, 1)
    if int(ret) <= 32:
        print('[FAIL] user declined elevation')
        sys.exit(1)
    sys.exit(0)


def sha256(data: bytes | Path) -> str:
    h = hashlib.sha256()
    if isinstance(data, Path):
        with data.open('rb') as f:
            for chunk in iter(lambda: f.read(1 << 16), b''):
                h.update(chunk)
    else:
        h.update(data)
    return h.hexdigest()


def lm_studio_installed() -> bool:
    return ICON_TARGET.exists()


def cmd_apply() -> int:
    if not lm_studio_installed():
        print('[WARN] LM Studio not installed - nothing to patch')
        return 2
    ico_bytes = render_ico()
    if sha256(ICON_TARGET) == sha256(ico_bytes):
        print('[PASS] already white - nothing to do')
        return 0
    require_admin('apply')
    if not ICON_BACKUP.exists():
        shutil.copy2(ICON_TARGET, ICON_BACKUP)
        print(f'[PASS] backup: {ICON_BACKUP}')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.ico') as tmp:
        tmp.write(ico_bytes)
        tmp_path = Path(tmp.name)
    try:
        shutil.copy2(tmp_path, ICON_TARGET)
    finally:
        tmp_path.unlink(missing_ok=True)
    print(f'[PASS] replaced: {ICON_TARGET} ({len(ico_bytes)} bytes)')
    print('[INFO] fully quit LM Studio from the tray and relaunch to see the change')
    return 0


def cmd_restore() -> int:
    if not ICON_BACKUP.exists():
        print('[WARN] no backup found - nothing to restore')
        return 0
    require_admin('restore')
    shutil.copy2(ICON_BACKUP, ICON_TARGET)
    print(f'[PASS] restored original: {ICON_TARGET}')
    return 0


def cmd_status() -> int:
    if not lm_studio_installed():
        print('[WARN] LM Studio not installed')
        return 2
    ico_bytes = render_ico()
    t_hash = sha256(ICON_TARGET)
    w_hash = sha256(ico_bytes)
    matched = t_hash == w_hash
    print(f'icon.ico       : {ICON_TARGET}')
    print(f'  state        : {"white-patched" if matched else "original / colored"}')
    print(f'  sha256 now   : {t_hash}')
    print(f'  sha256 white : {w_hash}')
    print(f'backup exists  : {ICON_BACKUP.exists()}')
    return 0


COMMANDS = {
    'apply':   cmd_apply,
    'restore': cmd_restore,
    'status':  cmd_status,
}


def main() -> int:
    if sys.platform != 'win32':
        print('[FAIL] Windows-only')
        return 1
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        return 1
    return COMMANDS[sys.argv[1]]()


if __name__ == '__main__':
    sys.exit(main())
