"""Flow: png → resize → enhance → watermark → to-webp → exif read.

Each stage writes to its own output path so all artifacts are inspectable
after the run (helpful for debugging visual regressions).
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from .._helpers import (
    assert_image_dims,
    assert_image_format,
    invoke_subprocess,
)

pytestmark = pytest.mark.flow


def _ok(res) -> None:
    assert res.exit_code == 0, f"exit {res.exit_code}\n{res.output}"


class TestFlowImagePipeline:
    @pytest.fixture(scope="class")
    def workspace(self):
        tmp = Path(tempfile.mkdtemp(prefix="claw_flow_img_"))
        from PIL import Image
        src = tmp / "src.png"
        Image.new("RGB", (800, 600), (50, 100, 200)).save(src, format="PNG")
        ws = {"tmp": tmp, "src": src,
              "resized": tmp / "resized.png",
              "enhanced": tmp / "enhanced.png",
              "watermarked": tmp / "wm.png",
              "webp": tmp / "out.webp",
              "jpeg": tmp / "out.jpg"}
        yield ws
        shutil.rmtree(tmp, ignore_errors=True)

    def test_01_resize(self, workspace: dict) -> None:
        _ok(invoke_subprocess("img", "resize", str(workspace["src"]),
                              "--geometry", "400x300!",
                              "--out", str(workspace["resized"])))
        assert_image_dims(workspace["resized"], 400, 300)

    def test_02_enhance(self, workspace: dict) -> None:
        _ok(invoke_subprocess("img", "enhance", str(workspace["resized"]),
                              "--autocontrast", "--out", str(workspace["enhanced"])))
        assert workspace["enhanced"].exists()

    def test_03_watermark(self, workspace: dict) -> None:
        _ok(invoke_subprocess("img", "watermark", str(workspace["enhanced"]),
                              "--text", "DRAFT", "--position", "BR",
                              "--out", str(workspace["watermarked"])))

    def test_04_to_webp(self, workspace: dict) -> None:
        _ok(invoke_subprocess("img", "to-webp", str(workspace["watermarked"]),
                              "--quality", "80", "--out", str(workspace["webp"])))
        assert_image_format(workspace["webp"], "WEBP")

    def test_05_to_jpeg(self, workspace: dict) -> None:
        _ok(invoke_subprocess("img", "to-jpeg", str(workspace["watermarked"]),
                              "--bg", "white", "--quality", "85",
                              "--out", str(workspace["jpeg"])))
        assert_image_format(workspace["jpeg"], "JPEG")

    def test_06_exif_read(self, workspace: dict) -> None:
        # JPEG was just written by Pillow without EXIF — verb should still
        # exit cleanly.
        res = invoke_subprocess("img", "exif", str(workspace["jpeg"]), "--json")
        _ok(res)
