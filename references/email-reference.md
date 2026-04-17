# Email / MIME Composition + Gmail CLI Reference

> **TL;DR: use `claw email <verb>` for common tasks.** See [references/claw/email.md](claw/email.md). This reference documents the library API (Python `email.mime`) and raw `gws gmail` surface for escape-hatch / advanced workflows not covered by `claw email` — mail-merge with per-recipient variables, iCalendar invites, S/MIME / PGP, label mutations, batch message delete, streaming new-email watchers, and the Gmail API auth model.

## Contents

- **SEND / REPLY / FORWARD** *(covered by `claw email send/reply/forward/draft`)*
  - [Helper commands (`+send`, `+triage`, `+reply`, `+forward`)](#gmail-cli-gws-gmail)
  - Full raw API: [gws-cli.md — Gmail](gws-cli.md#gmail)
- **BUILD MIME message directly** — Python `email.mime`
  - [Critical rules (encoding, Content-ID, Gmail gotchas)](#critical-rules)
  - [MIMEText, MIMEMultipart, attachments, inline images, headers, threading](#python-mime-emailmime)
- **Escape-hatch recipes** — [iCalendar invites, mail-merge, S/MIME, batch label ops](#escape-hatch-recipes)

## CRITICAL RULES

1. **For simple sends, prefer `claw email send`** — it does MIME assembly, base64url, and threading for you. This reference is for the escape hatches.
2. **MIME composition is Python code** — NOT a CLI command. Build the message in Python, then send via Gmail API.
3. **Gmail API send requires base64url encoding** — use `base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")`.
4. **Content-ID for inline images** must match the `cid:` reference in HTML exactly (including angle brackets in the header).
5. **Always set `"utf-8"` charset** on MIMEText to avoid encoding issues with non-ASCII characters.

### Common Mistakes

```
WRONG: MIMEText("Hello")                              # Missing subtype and charset
WRONG: MIMEText("Hello", "text")                       # Subtype is "plain" not "text"
WRONG: base64.b64encode(msg.as_bytes())                # Gmail needs urlsafe, not standard
WRONG: img.add_header("Content-ID", "logo_id")         # Missing angle brackets

RIGHT: MIMEText("Hello", "plain", "utf-8")
RIGHT: MIMEText("<b>Hi</b>", "html", "utf-8")
RIGHT: base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
RIGHT: img.add_header("Content-ID", "<logo_id>")       # Angle brackets required
```

---

## Python MIME (email.mime)

### Imports
```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email import encoders
import base64
```

### MIMEText — Create a text message part

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `_text` | string | YES | — | The text content |
| `_subtype` | string | no | `"plain"` | `"plain"` or `"html"` |
| `_charset` | string | no | `"us-ascii"` | Always use `"utf-8"` |

```python
msg = MIMEText("Hello", "plain", "utf-8")
msg = MIMEText("<h1>Hello</h1>", "html", "utf-8")
```

### MIMEMultipart — container subtypes

| Subtype | Purpose | When to use |
|---------|---------|-------------|
| `"mixed"` | Attachments alongside text body | Email with file attachments |
| `"alternative"` | Multiple representations (plain + HTML) | Email with both plain text and HTML versions |
| `"related"` | HTML with inline images (Content-ID refs) | HTML email with embedded images |

### Attachments

`MIMEBase` + `encoders.encode_base64` is the general form; `MIMEApplication` is the shortcut for the common case.

```python
with open("report.xlsx", "rb") as f:
    part = MIMEApplication(f.read(), Name="report.xlsx")
    part["Content-Disposition"] = 'attachment; filename="report.xlsx"'
    msg.attach(part)
```

### Headers

| Header | Purpose | Example |
|--------|---------|---------|
| `To` | Primary recipients | `msg["To"] = "a@x.com, b@x.com"` |
| `From` | Sender | `msg["From"] = "me@x.com"` |
| `Cc` | Carbon copy | `msg["Cc"] = "c@x.com"` |
| `Bcc` | Blind carbon copy | `msg["Bcc"] = "d@x.com"` |
| `Subject` | Subject line | `msg["Subject"] = "Report"` |
| `Reply-To` | Reply address | `msg["Reply-To"] = "reply@x.com"` |
| `In-Reply-To` | Message being replied to | `msg["In-Reply-To"] = "<msgid@x.com>"` |
| `References` | Thread chain | `msg["References"] = "<id1> <id2>"` |
| `Date` | Send date | `msg["Date"] = email.utils.formatdate(localtime=True)` |
| `Message-ID` | Unique message ID | `msg["Message-ID"] = email.utils.make_msgid()` |

### Gmail API Raw Format (base64url)

```python
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
# {"raw": raw} in Gmail API send
```

### Inline image pattern (Content-ID)

The `cid:` in the HTML must exactly match the `Content-ID` header (angle-bracket-wrapped).

```python
msg = MIMEMultipart("related")
msg.attach(MIMEText('<img src="cid:chart_img">', "html"))
with open("chart.png", "rb") as f:
    img = MIMEImage(f.read(), _subtype="png")
    img.add_header("Content-ID", "<chart_img>")
    img.add_header("Content-Disposition", "inline", filename="chart.png")
    msg.attach(img)
```

### Reply threading

For Gmail API, set `threadId` in the send request **and** set `In-Reply-To` + `References`:

```python
msg["In-Reply-To"] = original_message_id        # "<original-id@mail.gmail.com>"
msg["References"] = f"{original_references} {original_message_id}"
msg["Subject"] = "Re: Original Subject"
# Gmail API: {"raw": raw, "threadId": "thread_id_here"}
```

---

## Gmail CLI (gws gmail)

All raw Gmail API commands live under `gws gmail users ...` and take `userId` in the `--params` JSON (use `"me"` for the authenticated user). Request bodies go in `--json`. When in doubt, run `gws gmail users <resource> <method> --help`.

> **Windows note:** `gws` is a `.cmd` shim on Windows. When calling it from Python `subprocess.run([...])` without `shell=True`, resolve the full path first: `GWS = shutil.which("gws") or "gws"`. Otherwise you'll get `FileNotFoundError`.

### Convenience helpers (no MIME plumbing required)

```bash
# Send a new email
gws gmail +send --to alice@x.com --subject 'Hi' --body 'Hello'
gws gmail +send --to alice@x.com --subject 'Hi' --body '<b>Hi</b>' --html
gws gmail +send --to a@x.com --cc b@x.com --bcc c@x.com --subject S --body B --dry-run

# Triage unread inbox (read-only summary)
gws gmail +triage
gws gmail +triage --max 5 --query 'from:boss@x.com' --labels
gws gmail +triage --format json | jq '.[].subject'

# Reply / reply-all / forward (threading handled automatically)
gws gmail +reply     --message-id <MESSAGE_ID> --body 'Thanks!'
gws gmail +reply-all --message-id <MESSAGE_ID> --body 'Sounds good' --remove bob@x.com
gws gmail +forward   --message-id <MESSAGE_ID> --to dave@x.com --body 'FYI'
```

For attachments, custom headers, or batch operations, fall through to the raw API.

> Full Gmail API command reference (messages, drafts, labels, threads, attachments, history, search operators): [gws-cli.md — Gmail](gws-cli.md#gmail).

### Scope model (Gmail API)

| Scope | Enables |
|---|---|
| `gmail.send` | Send only. Cannot read. |
| `gmail.readonly` | Read messages, search, list labels/threads. Does **not** reliably fetch attachment bodies on some org tenants. |
| `gmail.modify` | Read + label mutation + attachment download (org-portable). Required for `claw email download-attachment` on most tenants. |
| `gmail.labels` | Label CRUD only. |
| `gmail.compose` | Draft creation only. |

`gmail.send` does **not** imply `gmail.readonly`. Replies, forwards, and search need their own scopes. `claw doctor` prompts to re-login when a scope is missing. Gmail API enablement in Cloud Console is a separate step from the OAuth consent screen.

---

## Escape-hatch recipes

The snippets below are what `claw email` explicitly doesn't wrap. Use them when the CLI flag surface can't express what you need.

### 1. Calendar invite (iCalendar `METHOD:REQUEST`)

`claw email` has no `text/calendar` surface. Build it by hand:

```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ical = (
    "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nMETHOD:REQUEST\r\n"
    "BEGIN:VEVENT\r\nUID:evt-123@x.com\r\nSUMMARY:Kickoff\r\n"
    "DTSTART:20260420T140000Z\r\nDTEND:20260420T150000Z\r\n"
    "ORGANIZER:mailto:me@x.com\r\nATTENDEE;RSVP=TRUE:mailto:alice@x.com\r\n"
    "END:VEVENT\r\nEND:VCALENDAR\r\n"
)
msg = MIMEMultipart("mixed")
msg.attach(MIMEText("Kickoff invite attached.", "plain", "utf-8"))
cal_part = MIMEText(ical, "calendar", "utf-8")
cal_part.replace_header("Content-Type", 'text/calendar; charset="utf-8"; method=REQUEST')
msg.attach(cal_part)
```

### 2. Mail-merge with per-recipient variables + 429 backoff

`claw email send` sends one RFC 2822 per call. Loop with jittered backoff for bulk sends — Gmail rate-limits at around 250 messages/day for personal and tighter bursts per minute:

```python
import time, random, subprocess, json

for row in recipients:                      # each row: {"to": ..., "name": ...}
    body = template.format(**row)
    for attempt in range(5):
        p = subprocess.run(
            ["claw", "email", "send", "--to", row["to"],
             "--subject", "Hi", "--body", body, "--json"],
            capture_output=True, text=True,
        )
        if p.returncode == 0:
            break
        err = json.loads(p.stderr or "{}")
        if err.get("code") != "RATE_LIMIT":
            raise RuntimeError(err)
        time.sleep((2 ** attempt) + random.random())
```

### 3. S/MIME signed body (`multipart/signed`)

```python
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
# sig_bytes = PKCS#7 detached signature over body.as_bytes()
signed = MIMEMultipart("signed", protocol="application/pkcs7-signature",
                       micalg="sha-256")
signed.attach(body)
sig = MIMEApplication(sig_bytes, _subtype="pkcs7-signature", name="smime.p7s")
sig["Content-Disposition"] = 'attachment; filename="smime.p7s"'
signed.attach(sig)
```

### 4. Batch label mutation on fetched messages

`claw email` doesn't mutate labels. Use `gws` directly:

```bash
gws gmail users messages batchModify \
  --params '{"userId":"me"}' \
  --json '{"ids":["18e2f3a","18e2f3b"],"addLabelIds":["Label_123"],"removeLabelIds":["INBOX"]}'
```

### 5. Streaming new-email watcher (long-running)

Gmail push → Pub/Sub is the scalable path; for small workloads, the `+watch` helper emits NDJSON as new messages arrive:

```bash
gws gmail +watch --query 'is:unread newer_than:1h' --format json \
  | while read line; do echo "$line" | jq '.subject'; done
```
