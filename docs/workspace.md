# Workspace — Google Workspace CLI

> `gws` CLI for Drive, Sheets, Docs, Slides, Gmail, Calendar, Tasks. Authenticated and ready.

**Related:** [mailbox.md](mailbox.md) | [doc-forge.md](doc-forge.md) | [pipelines.md](pipelines.md)

---

## Drive

```bash
# Search files
gws drive files list --params '{"q":"name contains \"report\"","pageSize":10}'
gws drive files list --params '{"q":"mimeType=\"application/vnd.google-apps.folder\"","pageSize":50}'

# Download
gws drive files get --params '{"fileId":"ID","alt":"media"}' --output ./file.xlsx

# Upload new
gws drive files create --upload ./file.pdf \
  --upload-content-type application/pdf \
  --json '{"name":"file.pdf","parents":["FOLDER_ID"]}'

# Update existing (overwrite content)
gws drive files update --params '{"fileId":"ID"}' \
  --upload ./file.xlsx \
  --upload-content-type application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

# Delete
gws drive files delete --params '{"fileId":"ID"}'

# Export Google format → standard format
gws drive files export --params '{"fileId":"ID","mimeType":"application/pdf"}' --output ./out.pdf

# Share (anyone with link)
gws drive permissions create --params '{"fileId":"ID"}' --json '{"role":"reader","type":"anyone"}'

# Create folder
gws drive files create --json '{"name":"Folder","mimeType":"application/vnd.google-apps.folder","parents":["PARENT_ID"]}'

# Move file between folders
gws drive files update --params '{"fileId":"FILE_ID","addParents":"NEW_FOLDER","removeParents":"OLD_FOLDER"}'
```

## Sheets

```bash
# Create
gws sheets spreadsheets create --json '{"properties":{"title":"Sheet Name"}}'

# Read range
gws sheets spreadsheets values get --params '{"spreadsheetId":"ID","range":"Sheet1!A1:Z100"}'

# Write (overwrite)
gws sheets spreadsheets values update \
  --params '{"spreadsheetId":"ID","range":"A1","valueInputOption":"USER_ENTERED"}' \
  --json '{"values":[["Header1","Header2"],["val1","val2"]]}'

# Append rows
gws sheets spreadsheets values append \
  --params '{"spreadsheetId":"ID","range":"A1","valueInputOption":"USER_ENTERED"}' \
  --json '{"values":[["new","row"]]}'

# Clear range
gws sheets spreadsheets values clear --params '{"spreadsheetId":"ID","range":"Sheet1!A1:Z100"}'

# Batch update (formatting, new sheets, charts)
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId":"ID"}' \
  --json '{"requests":[{"addSheet":{"properties":{"title":"New Tab"}}}]}'
```

## Docs

```bash
# Create
gws docs documents create --json '{"title":"Doc Title"}'

# Read
gws docs documents get --params '{"documentId":"ID"}'

# Insert text
gws docs documents batchUpdate --params '{"documentId":"ID"}' \
  --json '{"requests":[{"insertText":{"location":{"index":1},"text":"Hello\n"}}]}'

# Insert heading
gws docs documents batchUpdate --params '{"documentId":"ID"}' \
  --json '{"requests":[
    {"insertText":{"location":{"index":1},"text":"Heading\n"}},
    {"updateParagraphStyle":{"range":{"startIndex":1,"endIndex":9},
      "paragraphStyle":{"namedStyleType":"HEADING_1"},"fields":"namedStyleType"}}
  ]}'

# Insert table
gws docs documents batchUpdate --params '{"documentId":"ID"}' \
  --json '{"requests":[{"insertTable":{"rows":3,"columns":3,"location":{"index":1}}}]}'
```

## Slides

```bash
# Create
gws slides presentations create --json '{"title":"Deck Title"}'

# Read
gws slides presentations get --params '{"presentationId":"ID"}'

# Add slide
gws slides presentations batchUpdate --params '{"presentationId":"ID"}' \
  --json '{"requests":[{"createSlide":{"insertionIndex":1,
    "slideLayoutReference":{"predefinedLayout":"TITLE_AND_BODY"}}}]}'

# Insert text into element
gws slides presentations batchUpdate --params '{"presentationId":"ID"}' \
  --json '{"requests":[{"insertText":{"objectId":"ELEMENT_ID","text":"Content"}}]}'

# Template merge (replace placeholders)
gws slides presentations batchUpdate --params '{"presentationId":"ID"}' \
  --json '{"requests":[{"replaceAllText":{
    "containsText":{"text":"{{placeholder}}","matchCase":true},
    "replaceText":"Actual Value"}}]}'
```

## Gmail

See [mailbox.md](mailbox.md) for composition & MIME. CLI quick reference:

```bash
# List (with search)
gws gmail users messages list --params '{"userId":"me","q":"is:unread newer_than:1d","maxResults":20}'

# Read (full)
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"full"}'

# Read (metadata only — fast)
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"metadata",
  "metadataHeaders":["From","To","Subject","Date"]}'

# Send (base64 RFC 2822)
gws gmail users messages send --params '{"userId":"me"}' --json '{"raw":"BASE64"}'

# Reply to thread
gws gmail users messages send --params '{"userId":"me"}' --json '{"raw":"BASE64","threadId":"THREAD_ID"}'

# Labels & marking
gws gmail users labels list --params '{"userId":"me"}'
gws gmail users messages modify --params '{"userId":"me","id":"MSG_ID"}' --json '{"removeLabelIds":["UNREAD"]}'

# Download attachment
gws gmail users messages attachments get \
  --params '{"userId":"me","messageId":"MSG_ID","id":"ATT_ID"}' --output ./file.pdf
```

**Search operators:** `from:` `to:` `subject:` `has:attachment` `is:unread` `newer_than:1d` `older_than:7d` `label:` `in:inbox` `filename:pdf` `larger:5M`

## Calendar

```bash
# List upcoming
gws calendar events list --params '{"calendarId":"primary",
  "timeMin":"2026-03-25T00:00:00Z","maxResults":10,"orderBy":"startTime","singleEvents":true}'

# Create event
gws calendar events insert --params '{"calendarId":"primary"}' \
  --json '{"summary":"Meeting","start":{"dateTime":"2026-03-26T10:00:00+05:30"},
  "end":{"dateTime":"2026-03-26T11:00:00+05:30"},"attendees":[{"email":"x@example.com"}]}'

# All-day event
gws calendar events insert --params '{"calendarId":"primary"}' \
  --json '{"summary":"Deadline","start":{"date":"2026-03-30"},"end":{"date":"2026-03-31"}}'

# Recurring
gws calendar events insert --params '{"calendarId":"primary"}' \
  --json '{"summary":"Standup","recurrence":["RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"],
  "start":{"dateTime":"2026-03-26T09:00:00+05:30"},"end":{"dateTime":"2026-03-26T09:15:00+05:30"}}'

# Update / Delete
gws calendar events patch --params '{"calendarId":"primary","eventId":"ID"}' --json '{"summary":"New Title"}'
gws calendar events delete --params '{"calendarId":"primary","eventId":"ID"}'
```

## Tasks

```bash
gws tasks tasklists list
gws tasks tasks list --params '{"tasklist":"LIST_ID"}'
gws tasks tasks insert --params '{"tasklist":"LIST_ID"}' --json '{"title":"Task","due":"2026-03-30T00:00:00Z"}'
gws tasks tasks patch --params '{"tasklist":"LIST_ID","task":"TASK_ID"}' --json '{"status":"completed"}'
```

## CLI Flags

| Flag | Purpose |
|------|---------|
| `--format table\|csv\|yaml\|json` | Output format |
| `--page-all` | Auto-paginate (NDJSON) |
| `--upload <PATH>` | Attach file for upload |
| `--output <PATH>` | Save binary to file |
