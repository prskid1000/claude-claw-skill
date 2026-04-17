"""Selectors: PageSelector (pdf/doc), RangeSelector (excel), NodeSelector (CSS/XPath)."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class PageSelector:
    """pdftk/qpdf-style page-range parser.

    Accepts: `1`, `1-5`, `1,3,5`, `1-5,7,9-end`, `all`, `odd`, `even`, `z-1` (reverse).
    """

    raw: str

    def resolve(self, total: int) -> list[int]:
        """Return 1-indexed page numbers resolved against `total` pages."""
        spec = (self.raw or "all").strip().lower()
        out: list[int] = []

        if spec == "all":
            return list(range(1, total + 1))
        if spec == "odd":
            return [p for p in range(1, total + 1) if p % 2 == 1]
        if spec == "even":
            return [p for p in range(1, total + 1) if p % 2 == 0]
        if spec in ("z-1", "reverse"):
            return list(range(total, 0, -1))

        for part in spec.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, b = part.split("-", 1)
                start = total if a == "end" else int(a)
                stop = total if b == "end" else int(b)
                step = 1 if start <= stop else -1
                out.extend(range(start, stop + step, step))
            else:
                n = total if part == "end" else int(part)
                out.append(n)

        seen = set()
        result = []
        for p in out:
            if 1 <= p <= total and p not in seen:
                seen.add(p)
                result.append(p)
        return result


@dataclass
class RangeSelector:
    """Excel A1-notation parser. Returns (min_row, min_col, max_row, max_col), all 1-indexed."""

    raw: str

    def resolve(self) -> tuple[int, int, int | None, int | None]:
        spec = self.raw.strip().upper()
        m = re.match(r"^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$", spec)
        if not m:
            raise ValueError(f"invalid A1 range: {self.raw!r}")
        c1, r1, c2, r2 = m.groups()
        return (int(r1), _col_to_num(c1),
                int(r2) if r2 else None,
                _col_to_num(c2) if c2 else None)


def _col_to_num(col: str) -> int:
    n = 0
    for ch in col:
        n = n * 26 + (ord(ch) - 64)
    return n


@dataclass
class NodeSelector:
    """CSS-vs-XPath auto-detect selector for HTML/XML."""

    raw: str

    @property
    def kind(self) -> str:
        return "xpath" if self.raw.startswith(("/", ".")) else "css"
