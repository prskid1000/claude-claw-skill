"""Flow: mp4 → trim → scale → thumbnail → extract-audio → gif. Requires ffmpeg."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from .._helpers import (
    invoke_subprocess,
    require_tool,
)

pytestmark = pytest.mark.flow


def _ok(res) -> None:
    assert res.exit_code == 0, f"exit {res.exit_code}\n{res.output}"


class TestFlowMediaPipeline:
    @pytest.fixture(scope="class")
    def workspace(self):
        tmp = Path(tempfile.mkdtemp(prefix="claw_flow_media_"))
        require_tool("ffmpeg")
        src = tmp / "src.mp4"
        # 3-second blue clip with audio.
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-f", "lavfi", "-i", "color=c=blue:s=128x128:d=3",
             "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
             "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-shortest", str(src)],
            check=True,
        )
        ws = {"tmp": tmp, "src": src,
              "trimmed": tmp / "trim.mp4",
              "scaled": tmp / "scaled.mp4",
              "thumb": tmp / "thumb.png",
              "audio": tmp / "audio.mp3",
              "gif": tmp / "out.gif"}
        yield ws
        shutil.rmtree(tmp, ignore_errors=True)

    def test_01_trim(self, workspace: dict) -> None:
        _ok(invoke_subprocess("media", "trim", str(workspace["src"]),
                              "--from", "0", "--to", "1",
                              "--out", str(workspace["trimmed"])))
        assert workspace["trimmed"].exists()

    def test_02_scale(self, workspace: dict) -> None:
        _ok(invoke_subprocess("media", "scale", str(workspace["trimmed"]),
                              "--geometry", "64x64",
                              "--out", str(workspace["scaled"])))

    def test_03_thumbnail(self, workspace: dict) -> None:
        _ok(invoke_subprocess("media", "thumbnail", str(workspace["src"]),
                              "--at", "0:00:01",
                              "--out", str(workspace["thumb"])))
        assert workspace["thumb"].exists()

    def test_04_extract_audio(self, workspace: dict) -> None:
        _ok(invoke_subprocess("media", "extract-audio", str(workspace["src"]),
                              "--format", "mp3",
                              "--out", str(workspace["audio"])))
        assert workspace["audio"].exists()

    def test_05_gif(self, workspace: dict) -> None:
        _ok(invoke_subprocess("media", "gif", str(workspace["src"]),
                              "--start", "0", "--duration", "1",
                              "--width", "64", "--fps", "10",
                              "--out", str(workspace["gif"])))
        assert workspace["gif"].exists()

    def test_06_info(self, workspace: dict) -> None:
        require_tool("ffprobe")
        res = invoke_subprocess("media", "info", str(workspace["src"]), "--json")
        _ok(res)
