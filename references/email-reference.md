# Email / MIME Composition + Gmail CLI Reference

## Contents
- [CRITICAL RULES](#critical-rules)
- [Python MIME (email.mime)](#python-mime-emailmime)
- [Gmail CLI (gws gmail)](#gmail-cli-gws-gmail)

---

## CRITICAL RULES

1. **For simple emails, use `gws gmail +send`** — don't build MIME manually unless you need attachments or inline images.
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
WRONG: gws gmail users messages send ... --body "Hi"   # --body is for +send helper only

RIGHT: MIMEText("Hello", "plain", "utf-8")
RIGHT: MIMEText("<b>Hi</b>", "html", "utf-8")
RIGHT: base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
RIGHT: img.add_header("Content-ID", "<logo_id>")       # Angle brackets required
RIGHT: gws gmail +send --to user@x.com --subject 'Hi' --body 'Hello'
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

---

### MIMEText — Create a text message part

**Constructor:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `_text` | string | YES | — | The text content |
| `_subtype` | string | no | `"plain"` | `"plain"` or `"html"` |
| `_charset` | string | no | `"us-ascii"` | Always use `"utf-8"` |

```python
# Plain text
msg = MIMEText("Hello, world!", "plain", "utf-8")

# HTML
msg = MIMEText("<h1>Hello</h1><p>World</p>", "html", "utf-8")
```

---

### MIMEMultipart — Create a container for multiple parts

**Constructor:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `_subtype` | string | no | `"mixed"` | Container type (see table below) |

**Subtype values (choose the RIGHT one):**
| Subtype | Purpose | When to use |
|---------|---------|-------------|
| `"mixed"` | Attachments alongside text body | Email with file attachments |
| `"alternative"` | Multiple representations (plain + HTML) | Email with both plain text and HTML versions |
| `"related"` | HTML with inline images (Content-ID refs) | HTML email with embedded images |

```python
# Mixed (text + attachments)
msg = MIMEMultipart("mixed")
msg.attach(MIMEText("Body text", "plain"))

# Alternative (plain + HTML)
msg = MIMEMultipart("alternative")
msg.attach(MIMEText("Plain body", "plain"))
msg.attach(MIMEText("<h1>HTML body</h1>", "html"))

# Related (HTML with inline images)
msg = MIMEMultipart("related")
html = MIMEText('<img src="cid:logo_id">', "html")
msg.attach(html)
with open("logo.png", "rb") as f:
    img = MIMEImage(f.read())
    img.add_header("Content-ID", "<logo_id>")
    img.add_header("Content-Disposition", "inline", filename="logo.png")
    msg.attach(img)
```

---

### Attachments (MIMEBase + encode_base64)

```python
with open("report.pdf", "rb") as f:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename="report.pdf")
    msg.attach(part)
```

#### Shortcut with MIMEApplication
```python
with open("report.xlsx", "rb") as f:
    part = MIMEApplication(f.read(), Name="report.xlsx")
    part["Content-Disposition"] = 'attachment; filename="report.xlsx"'
    msg.attach(part)
```

---

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

---

### Gmail API Raw Format (base64url)

```python
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")
# Use as: {"raw": raw} in Gmail API send
```

---

### Multiple Attachments Pattern

```python
msg = MIMEMultipart("mixed")
msg["To"] = "recipient@example.com"
msg["From"] = "sender@example.com"
msg["Subject"] = "Monthly Reports"

# Body
msg.attach(MIMEText("Please find the reports attached.", "plain"))

# Attach multiple files
for filepath in ["report.pdf", "data.xlsx", "chart.png"]:
    with open(filepath, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment",
                        filename=os.path.basename(filepath))
        msg.attach(part)
```

---

### Inline Images (Content-ID for HTML email)

```python
msg = MIMEMultipart("related")

html_body = """\
<html>
<body>
  <h1>Report</h1>
  <img src="cid:chart_img">
  <p>See the chart above.</p>
</body>
</html>
"""
msg.attach(MIMEText(html_body, "html"))

with open("chart.png", "rb") as f:
    img = MIMEImage(f.read(), _subtype="png")
    img.add_header("Content-ID", "<chart_img>")
    img.add_header("Content-Disposition", "inline", filename="chart.png")
    msg.attach(img)
```

---

### Reply Threading

```python
# Replying to an existing message
original_message_id = "<original-id@mail.gmail.com>"
original_references = "<ref1@mail.gmail.com> <ref2@mail.gmail.com>"

msg["In-Reply-To"] = original_message_id
msg["References"] = f"{original_references} {original_message_id}"
msg["Subject"] = "Re: Original Subject"

# For Gmail API, also set threadId in the send request:
# {"raw": raw, "threadId": "thread_id_here"}
```

---

---

## Gmail CLI (gws gmail)

All raw Gmail API commands live under `gws gmail users ...` and take `userId` in the `--params` JSON (use `"me"` for the authenticated user). Request bodies go in `--json`. When in doubt, run `gws gmail users <resource> <method> --help`.

> **Windows note:** `gws` is a `.cmd` shim on Windows. When calling it from Python `subprocess.run([...])` without `shell=True`, resolve the full path first: `GWS = shutil.which("gws") or "gws"`. Otherwise you'll get `FileNotFoundError`.

### Convenience helpers (no MIME plumbing required)

For common flows, prefer these helpers over the raw API — they handle RFC 2822 / base64url / threading automatically:

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

> Full Gmail API command reference (messages, drafts, labels, threads, attachments, history, search operators): [gws-cli.md -- Gmail](gws-cli.md#gmail)
