"""Shared MIME-building helpers for the email verbs."""

from __future__ import annotations

import base64
import mimetypes
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path
from typing import Iterable


MIME_OVERRIDES: dict[str, tuple[str, str]] = {
    ".xlsx": ("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ".docx": ("application", "vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ".pptx": ("application", "vnd.openxmlformats-officedocument.presentationml.presentation"),
    ".eml":  ("message", "rfc822"),
    ".md":   ("text", "markdown"),
}


def _split_at_prefix(value: str) -> Path:
    """`@path/to/file` → Path; errors if missing prefix."""
    if not value.startswith("@"):
        raise ValueError(f"expected @-prefixed path, got {value!r}")
    return Path(value[1:])


def _guess_mime(path: Path, override: str | None = None) -> tuple[str, str]:
    if override:
        if "/" not in override:
            raise ValueError(f"bad --mime: {override}")
        return tuple(override.split("/", 1))  # type: ignore[return-value]
    ext = path.suffix.lower()
    if ext in MIME_OVERRIDES:
        return MIME_OVERRIDES[ext]
    t, _ = mimetypes.guess_type(str(path))
    if not t:
        return ("application", "octet-stream")
    return tuple(t.split("/", 1))  # type: ignore[return-value]


def _parse_attach(spec: str) -> tuple[Path, str | None]:
    """`@path` or `@path:mime/type` → (path, forced_mime)."""
    if ":" in spec and not spec[1:].startswith(("/", "\\")) and spec.count(":") >= 1:
        base, _, rest = spec.rpartition(":")
        if "/" in rest:
            return (_split_at_prefix(base), rest)
    return (_split_at_prefix(spec), None)


def _parse_addrs(values: Iterable[str]) -> list[str]:
    out: list[str] = []
    for v in values:
        for part in v.split(","):
            part = part.strip()
            if part:
                out.append(part)
    return out


def build_message(*, to: list[str], cc: list[str], bcc: list[str],
                  subject: str, body: str, html: str | None = None,
                  attachments: list[str] | None = None,
                  inline: list[str] | None = None,
                  from_addr: str | None = None,
                  reply_to: str | None = None,
                  headers: list[str] | None = None,
                  in_reply_to: str | None = None,
                  references: str | None = None) -> EmailMessage:
    """Assemble a full EmailMessage, incl. multipart/alternative + inline cids."""
    msg = EmailMessage()
    if to:
        msg["To"] = ", ".join(to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)
    msg["Subject"] = subject
    if from_addr:
        msg["From"] = from_addr
    if reply_to:
        msg["Reply-To"] = reply_to
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references
    for h in (headers or []):
        if "=" not in h:
            raise ValueError(f"--header must be KEY=VALUE, got {h!r}")
        k, _, v = h.partition("=")
        msg[k.strip()] = v.strip()

    msg.set_content(body or "", subtype="plain", charset="utf-8")

    if html:
        html_text = Path(html).read_text(encoding="utf-8")
        msg.add_alternative(html_text, subtype="html")
        if inline:
            html_part = msg.get_payload()[-1]
            for spec in inline:
                if "=" not in spec:
                    raise ValueError(f"--inline must be CID=@PATH, got {spec!r}")
                cid, _, pathspec = spec.partition("=")
                path = _split_at_prefix(pathspec)
                maintype, subtype = _guess_mime(path)
                cid_value = cid.strip()
                with path.open("rb") as f:
                    html_part.add_related(
                        f.read(), maintype=maintype, subtype=subtype,
                        cid=f"<{cid_value}>",
                    )

    for spec in (attachments or []):
        path, forced = _parse_attach(spec)
        maintype, subtype = _guess_mime(path, forced)
        with path.open("rb") as f:
            msg.add_attachment(
                f.read(), maintype=maintype, subtype=subtype, filename=path.name,
            )
    return msg


def to_raw_b64(msg: EmailMessage) -> str:
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")


__all__ = ["build_message", "to_raw_b64", "_parse_addrs", "_parse_attach"]
