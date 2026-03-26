# Google Workspace — `gws` Quick Reference

> `gws` CLI for Drive, Sheets, Docs, Slides, Gmail, Calendar, Tasks. Authenticated and ready.

**Related:** [email-workflows.md](email-workflows.md) | [create-documents.md](create-documents.md) | [data-pipelines.md](data-pipelines.md)

---

## General tips

- Prefer `--format json` when you want to pipe/parse.
- Keep params small (pageSize / maxResults) for quick exploration.

## Drive (minimal)

```bash
# List/search
gws drive files list --params '{"q":"name contains \"report\"","pageSize":10}'

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

# Share (anyone with link)
gws drive permissions create --params '{"fileId":"ID"}' --json '{"role":"reader","type":"anyone"}'

# Delete
gws drive files delete --params '{"fileId":"ID"}'

# Export Google format → standard format
gws drive files export --params '{"fileId":"ID","mimeType":"application/pdf"}' --output ./out.pdf
```

## Sheets (minimal)

```bash
# Create
gws sheets spreadsheets create --json '{"properties":{"title":"Sheet Name"}}'

# Read range
gws sheets spreadsheets values get --params '{"spreadsheetId":"ID","range":"Sheet1!A1:Z100"}'

# Write (overwrite)
gws sheets spreadsheets values update \
  --params '{"spreadsheetId":"ID","range":"A1","valueInputOption":"USER_ENTERED"}' \
  --json '{"values":[["Header1","Header2"],["val1","val2"]]}'

# Clear range
gws sheets spreadsheets values clear --params '{"spreadsheetId":"ID","range":"Sheet1!A1:Z100"}'
```

## Docs (minimal)

```bash
# Create
gws docs documents create --json '{"title":"Doc Title"}'

# Read
gws docs documents get --params '{"documentId":"ID"}'
```

## Slides (minimal)

```bash
# Create
gws slides presentations create --json '{"title":"Deck Title"}'

# Read
gws slides presentations get --params '{"presentationId":"ID"}'
```

## Gmail

See [email-workflows.md](email-workflows.md) for composition & MIME. CLI quick reference:

```bash
# List (with search)
gws gmail users messages list --params '{"userId":"me","q":"is:unread newer_than:1d","maxResults":20}'

# Read (metadata only — fast)
gws gmail users messages get --params '{"userId":"me","id":"MSG_ID","format":"metadata",
  "metadataHeaders":["From","To","Subject","Date"]}'

# Send (base64 RFC 2822)
gws gmail users messages send --params '{"userId":"me"}' --json '{"raw":"BASE64"}'
```

**Search operators:** `from:` `to:` `subject:` `has:attachment` `is:unread` `newer_than:1d` `older_than:7d` `label:` `in:inbox` `filename:pdf` `larger:5M`

## Calendar (minimal)

```bash
gws calendar events list --params '{"calendarId":"primary",
  "timeMin":"2026-03-25T00:00:00Z","maxResults":10,"orderBy":"startTime","singleEvents":true}'
```

## Tasks (minimal)

```bash
gws tasks tasklists list
gws tasks tasks list --params '{"tasklist":"LIST_ID"}'
gws tasks tasks insert --params '{"tasklist":"LIST_ID"}' --json '{"title":"Task","due":"2026-03-30T00:00:00Z"}'
```

## CLI Flags

| Flag | Purpose |
|------|---------|
| `--format table\|csv\|yaml\|json` | Output format |
| `--page-all` | Auto-paginate (NDJSON) |
| `--upload <PATH>` | Attach file for upload |
| `--output <PATH>` | Save binary to file |
