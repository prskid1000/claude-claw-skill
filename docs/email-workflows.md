# Email Workflows — Compose / Send / Attachments

> Compose emails with Python MIME, send/read via Gmail CLI, manage attachments and threads.

**Related:** [gws-quickref.md](gws-quickref.md) | [create-documents.md](create-documents.md) | [data-pipelines.md](data-pipelines.md)

---

## Composing Emails

### Text Email

```python
import base64
from email.mime.text import MIMEText

msg = MIMEText("Email body here")
msg['To'] = 'recipient@example.com'
msg['Subject'] = 'Subject line'
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
# → gws gmail users messages send --params '{"userId":"me"}' --json '{"raw":"<raw>"}'
```

### HTML Email

```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

msg = MIMEMultipart('alternative')
msg['To'] = 'recipient@example.com'
msg['Subject'] = 'Subject'
msg.attach(MIMEText("Plain text fallback", 'plain'))
msg.attach(MIMEText("<h1>Title</h1><p>Rich body</p>", 'html'))
raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
```

### With Attachment

```python
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import base64

msg = MIMEMultipart()
msg['To'] = 'recipient@example.com'
msg['Subject'] = 'Report attached'
msg.attach(MIMEText("Please find the report attached.", 'plain'))

with open('report.pdf', 'rb') as f:
    part = MIMEBase('application', 'pdf')
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename='report.pdf')
    msg.attach(part)

raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
```

### Multiple Attachments

```python
for filename, maintype, subtype in [
    ('report.pdf', 'application', 'pdf'),
    ('data.xlsx', 'application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    ('screenshot.png', 'image', 'png'),
]:
    with open(filename, 'rb') as f:
        part = MIMEBase(maintype, subtype)
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)
```

### Reply (preserve thread)

```python
msg['In-Reply-To'] = '<original-message-id>'
msg['References'] = '<original-message-id>'
# Send with threadId:
# --json '{"raw":"BASE64","threadId":"THREAD_ID"}'
```

## Gmail CLI

Full CLI reference in [gws-quickref.md](gws-quickref.md). Quick reference:

```bash
# Search
gws gmail users messages list --params '{"userId":"me","q":"QUERY","maxResults":N}'

# Read
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"full"}'

# Send
gws gmail users messages send --params '{"userId":"me"}' --json '{"raw":"BASE64"}'

# Mark read
gws gmail users messages modify --params '{"userId":"me","id":"MSG_ID"}' --json '{"removeLabelIds":["UNREAD"]}'

# Download attachment
gws gmail users messages attachments get \
  --params '{"userId":"me","messageId":"MSG_ID","id":"ATT_ID"}' --output ./file.pdf
```

## Search Operators

| Operator | Example | Purpose |
|----------|---------|---------|
| `from:` | `from:boss@company.com` | Sender |
| `to:` | `to:me` | Recipient |
| `subject:` | `subject:invoice` | Subject line |
| `has:attachment` | | Has files attached |
| `is:unread` | | Unread messages |
| `newer_than:` | `newer_than:1d` | Recent (1d, 7d, 1m) |
| `older_than:` | `older_than:30d` | Older than |
| `after:` / `before:` | `after:2026/03/01` | Date range |
| `label:` | `label:important` | By label |
| `filename:` | `filename:pdf` | Attachment type |
| `larger:` / `smaller:` | `larger:5M` | Size filter |
| `"exact phrase"` | `"project report"` | Exact match |

## Common Workflows

### Generate Report → Email It

```
1. Create doc with Python (see create-documents.md)
2. Compose email with attachment (see above)
3. gws gmail send
```

### Check Unread → Summarize

```
1. gws gmail list with q="is:unread newer_than:1d"
2. gws gmail get each with format=metadata
3. Summarize subjects/senders
```

### Download All Attachments

```
1. gws gmail get (full format)
2. Parse parts[] for attachmentId
3. gws gmail attachments get for each
```
