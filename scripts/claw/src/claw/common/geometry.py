"""ImageMagick geometry parser: `100x200`, `50%`, `100x200!`, `100x200>`, `100x200^`, `100x200+10+10`."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Geometry:
    width: int | None = None
    height: int | None = None
    pct: float | None = None
    force: bool = False       # `!`
    shrink_only: bool = False  # `>`
    enlarge_only: bool = False  # `<`
    fill_min: bool = False    # `^`
    offset: tuple[int, int] | None = None  # `+x+y`

    @classmethod
    def parse(cls, spec: str) -> "Geometry":
        s = spec.strip()
        if not s:
            return cls()
        off_match = re.search(r"([+-]\d+)([+-]\d+)$", s)
        offset = None
        if off_match:
            offset = (int(off_match.group(1)), int(off_match.group(2)))
            s = s[: off_match.start()]

        force = s.endswith("!"); s = s.rstrip("!")
        shrink_only = s.endswith(">"); s = s.rstrip(">")
        enlarge_only = s.endswith("<"); s = s.rstrip("<")
        fill_min = s.endswith("^"); s = s.rstrip("^")

        if s.endswith("%"):
            return cls(pct=float(s[:-1]), force=force, shrink_only=shrink_only,
                       enlarge_only=enlarge_only, fill_min=fill_min, offset=offset)
        if "x" in s:
            w, h = s.split("x", 1)
            return cls(width=int(w) if w else None,
                       height=int(h) if h else None,
                       force=force, shrink_only=shrink_only,
                       enlarge_only=enlarge_only, fill_min=fill_min, offset=offset)
        return cls(width=int(s) if s else None,
                   force=force, shrink_only=shrink_only,
                   enlarge_only=enlarge_only, fill_min=fill_min, offset=offset)

    def apply_to(self, w: int, h: int) -> tuple[int, int]:
        """Resolve against a source size; returns (new_w, new_h)."""
        if self.pct is not None:
            return (int(w * self.pct / 100), int(h * self.pct / 100))
        tw, th = self.width, self.height
        if tw is None and th is None:
            return (w, h)
        if self.force:
            return (tw or w, th or h)
        if tw is not None and th is not None:
            if self.fill_min:
                scale = max(tw / w, th / h)
            else:
                scale = min(tw / w, th / h)
            new = (int(w * scale), int(h * scale))
        elif tw is not None:
            new = (tw, int(h * tw / w))
        else:
            assert th is not None
            new = (int(w * th / h), th)
        if self.shrink_only and (new[0] > w or new[1] > h):
            return (w, h)
        if self.enlarge_only and (new[0] < w or new[1] < h):
            return (w, h)
        return new
