# Google Workspace CLI (`gws`) Reference

Complete command reference for the `gws` CLI tool (version **0.16.0**). Covers Drive, Sheets, Docs, Slides, Gmail, Calendar, and Tasks.

---

## Convention (READ FIRST)

`gws` 0.16.0 does **not** accept resource IDs as positional arguments. Every path/ID must be passed inside the `--params` JSON object. Key rules:

1. **IDs go inside `--params`**, never as bare positional args.
   - Wrong: `gws drive files get <FILE_ID>`
   - Right: `gws drive files get --params '{"fileId": "<FILE_ID>"}'`
2. **Gmail commands require the `users` sub-resource** and `"userId": "me"` in params.
   - Wrong: `gws gmail messages list --params '{"q":"is:unread"}'`
   - Right: `gws gmail users messages list --params '{"userId":"me","q":"is:unread"}'`
3. **Sheet values live under `sheets spreadsheets values`**, not `sheets values`.
   - Wrong: `gws sheets values get ...`
   - Right: `gws sheets spreadsheets values get --params '{"spreadsheetId":"...","range":"..."}'`
4. **Param names follow the Google Discovery API** path parameter names exactly: `fileId`, `spreadsheetId`, `documentId`, `presentationId`, `pageObjectId`, `calendarId`, `eventId`, `driveId`, `permissionId`, `commentId`, `replyId`, `revisionId`, `tasklist`, `task`, `userId`, `id` (Gmail drafts/labels/threads), `setting`, `sheetId`.
5. **`drive.comments.list` requires `fields`** — pass `"fields": "*"` (or a specific field mask) inside params.
6. **General syntax:**
   ```
   gws <service> <resource> [sub-resource] <method> [--params '{...}'] [--json '{...}'] [FLAGS]
   ```
7. Use `gws schema <service>.<resource>.<method>` to inspect exact parameter/body shapes. The `--help` output on any leaf command is authoritative.

### Windows / Python note

On Windows, `gws` is installed as a `.cmd` shim, so calling it from Python via `subprocess.run(["gws", ...])` will fail with `FileNotFoundError` unless you either:

- pass `shell=True`: `subprocess.run("gws drive files list --format json", shell=True, ...)`, or
- resolve the shim first: `subprocess.run([shutil.which("gws"), "drive", "files", "list"], ...)`.

---

## Global CLI Flags

| Flag | Purpose |
|------|---------|
| `--params '{...}'` | URL/path/query parameters as a JSON object (holds **all** IDs) |
| `--json '{...}'` | Request body as a JSON object (POST/PATCH/PUT) |
| `--format json\|table\|yaml\|csv` | Set output format (default: json) |
| `--page-all` | Auto-paginate through all results (streams NDJSON) |
| `--page-limit <N>` | Max pages with `--page-all` (default 10) |
| `--page-delay <MS>` | Delay between pages in ms (default 100) |
| `--upload <PATH>` | Attach a local file for upload |
| `--upload-content-type <MIME>` | MIME type of the uploaded file |
| `--output <PATH>` | Save binary response body to a local file |
| `--api-version <VER>` | Override the API version (e.g. v2, v3) |
| `--dry-run` | Validate locally without sending |

---

## Ergonomic `+helper` Commands

`gws` ships a set of high-level helpers (prefixed with `+`) that wrap common workflows. Prefer these when you don't need raw API control — they handle RFC 2822 / base64 / threading / MIME detection for you.

| Helper | One-liner | Example |
|---|---|---|
| `gws drive +upload <file>` | Upload a local file with auto-detected MIME and filename. | `gws drive +upload ./report.pdf --parent <FOLDER_ID>` |
| `gws gmail +send` | Send a plain-text or HTML email. | `gws gmail +send --to alice@example.com --subject 'Hi' --body 'Hello'` |
| `gws gmail +triage` | Read-only unread inbox summary (sender/subject/date). | `gws gmail +triage --max 10 --query 'from:boss'` |
| `gws gmail +reply` | Reply to a message (auto In-Reply-To / References / threadId). | `gws gmail +reply --message-id <MSG_ID> --body 'Thanks!'` |
| `gws gmail +reply-all` | Reply-all; supports `--remove` to drop recipients. | `gws gmail +reply-all --message-id <MSG_ID> --body 'ack' --remove bob@example.com` |
| `gws gmail +forward` | Forward a message with optional note. | `gws gmail +forward --message-id <MSG_ID> --to dave@example.com --body 'FYI'` |
| `gws gmail +watch` | Stream new emails as NDJSON. | `gws gmail +watch` |
| `gws sheets +append` | Append a row (CSV string or JSON array of rows). | `gws sheets +append --spreadsheet <SSID> --values 'Alice,100,true'` |
| `gws sheets +read` | Read a range, read-only. | `gws sheets +read --spreadsheet <SSID> --range 'Sheet1!A1:D10'` |
| `gws docs +write` | Append text to a Google Doc. | `gws docs +write --document <DOC_ID> --text 'New paragraph'` |
| `gws calendar +insert` | Create a simple event on a calendar. | `gws calendar +insert --summary 'Standup' --start 2026-04-10T09:00:00-07:00 --end 2026-04-10T09:30:00-07:00` |
| `gws calendar +agenda` | Read-only upcoming events across calendars. | `gws calendar +agenda --today` |

Run `gws <service> +<helper> --help` for full option lists.

---

## Auth

```
gws auth login                    # OAuth2 browser flow
gws auth login --readonly         # Read-only scopes
gws auth login -s drive,gmail     # Restrict scope picker to listed services
gws auth status                   # Current auth state
gws auth logout                   # Clear saved creds and token cache
gws auth export                   # Print decrypted credentials to stdout
gws auth setup --project <GCP>    # Configure GCP project + OAuth client (needs gcloud)
```

---

## Drive

### files

#### list
List files in Drive. Use `--params` to pass `q`, `orderBy`, `pageSize`, `driveId`, `corpora`, etc.

```
gws drive files list --params '{"q": "mimeType=\"application/vnd.google-apps.spreadsheet\"", "pageSize": 10}'
gws drive files list --params '{"q": "name contains \"report\" and trashed = false"}' --page-all
gws drive files list --params '{"q": "\"<FOLDER_ID>\" in parents"}' --format json
```

#### get
Retrieve file metadata by ID.

```
gws drive files get --params '{"fileId": "<FILE_ID>"}'
gws drive files get --params '{"fileId": "<FILE_ID>", "fields": "id,name,mimeType,size,modifiedTime"}'
```

#### create
Create a new file. Provide metadata via `--json` and optionally upload content via `--upload`.

```
# Create an empty Google Doc
gws drive files create --json '{"name": "My Document", "mimeType": "application/vnd.google-apps.document"}'

# Create a folder
gws drive files create --json '{"name": "My Folder", "mimeType": "application/vnd.google-apps.folder"}'

# Upload a local file
gws drive files create --json '{"name": "report.xlsx", "parents": ["<FOLDER_ID>"]}' \
  --upload /tmp/report.xlsx \
  --upload-content-type "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Upload a PDF
gws drive files create --json '{"name": "invoice.pdf"}' \
  --upload /tmp/invoice.pdf \
  --upload-content-type "application/pdf"
```

#### update
Update file metadata and/or content. File ID goes in `--params`.

```
# Rename a file
gws drive files update --params '{"fileId": "<FILE_ID>"}' --json '{"name": "New Name"}'

# Replace file content
gws drive files update --params '{"fileId": "<FILE_ID>"}' \
  --upload /tmp/updated.xlsx \
  --upload-content-type "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Move a file to a different folder
gws drive files update --params '{"fileId": "<FILE_ID>", "addParents": "<NEW_FOLDER_ID>", "removeParents": "<OLD_FOLDER_ID>"}'
```

#### delete
Permanently delete a file (bypasses trash).

```
gws drive files delete --params '{"fileId": "<FILE_ID>"}'
```

#### copy
Copy a file. Provide new metadata in `--json`.

```
gws drive files copy --params '{"fileId": "<FILE_ID>"}' \
  --json '{"name": "Copy of Report", "parents": ["<FOLDER_ID>"]}'
```

#### export
Export a Google Workspace document to a different format. Both `fileId` and `mimeType` go in `--params`; save with `--output`.

```
# Export Google Doc as PDF
gws drive files export --params '{"fileId": "<FILE_ID>", "mimeType": "application/pdf"}' --output /tmp/doc.pdf

# Export Google Sheet as CSV
gws drive files export --params '{"fileId": "<FILE_ID>", "mimeType": "text/csv"}' --output /tmp/sheet.csv

# Export Google Slides as PDF
gws drive files export --params '{"fileId": "<FILE_ID>", "mimeType": "application/pdf"}' --output /tmp/slides.pdf

# Export Google Doc as DOCX
gws drive files export --params '{"fileId": "<FILE_ID>", "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}' --output /tmp/doc.docx
```

### permissions

#### create
Grant access to a file or folder.

```
gws drive permissions create --params '{"fileId": "<FILE_ID>"}' --json '{"role": "reader", "type": "anyone"}'
gws drive permissions create --params '{"fileId": "<FILE_ID>"}' --json '{"role": "writer", "type": "user", "emailAddress": "user@example.com"}'
gws drive permissions create --params '{"fileId": "<FILE_ID>"}' --json '{"role": "reader", "type": "domain", "domain": "example.com"}'
```

Roles: `owner`, `organizer`, `fileOrganizer`, `writer`, `commenter`, `reader`
Types: `user`, `group`, `domain`, `anyone`

#### list
List all permissions on a file.

```
gws drive permissions list --params '{"fileId": "<FILE_ID>"}'
```

#### get
Get a specific permission by ID.

```
gws drive permissions get --params '{"fileId": "<FILE_ID>", "permissionId": "<PERMISSION_ID>"}'
```

#### update
Update an existing permission (e.g. change role).

```
gws drive permissions update --params '{"fileId": "<FILE_ID>", "permissionId": "<PERMISSION_ID>"}' \
  --json '{"role": "writer"}'
```

#### delete
Revoke a permission.

```
gws drive permissions delete --params '{"fileId": "<FILE_ID>", "permissionId": "<PERMISSION_ID>"}'
```

### comments

> Note: `comments list` **requires** a `fields` parameter. Use `"fields": "*"` for everything.

#### list
```
gws drive comments list --params '{"fileId": "<FILE_ID>", "fields": "*"}'
```

#### get
```
gws drive comments get --params '{"fileId": "<FILE_ID>", "commentId": "<COMMENT_ID>", "fields": "*"}'
```

#### create
```
gws drive comments create --params '{"fileId": "<FILE_ID>", "fields": "*"}' \
  --json '{"content": "Please review this section."}'
```

#### update
```
gws drive comments update --params '{"fileId": "<FILE_ID>", "commentId": "<COMMENT_ID>", "fields": "*"}' \
  --json '{"content": "Updated comment text."}'
```

#### delete
```
gws drive comments delete --params '{"fileId": "<FILE_ID>", "commentId": "<COMMENT_ID>"}'
```

### replies

#### list
```
gws drive replies list --params '{"fileId": "<FILE_ID>", "commentId": "<COMMENT_ID>", "fields": "*"}'
```

#### get
```
gws drive replies get --params '{"fileId": "<FILE_ID>", "commentId": "<COMMENT_ID>", "replyId": "<REPLY_ID>", "fields": "*"}'
```

#### create
```
gws drive replies create --params '{"fileId": "<FILE_ID>", "commentId": "<COMMENT_ID>", "fields": "*"}' \
  --json '{"content": "Acknowledged."}'
```

#### update
```
gws drive replies update --params '{"fileId": "<FILE_ID>", "commentId": "<COMMENT_ID>", "replyId": "<REPLY_ID>", "fields": "*"}' \
  --json '{"content": "Updated reply."}'
```

#### delete
```
gws drive replies delete --params '{"fileId": "<FILE_ID>", "commentId": "<COMMENT_ID>", "replyId": "<REPLY_ID>"}'
```

### revisions

#### list
```
gws drive revisions list --params '{"fileId": "<FILE_ID>"}'
```

#### get
```
gws drive revisions get --params '{"fileId": "<FILE_ID>", "revisionId": "<REVISION_ID>"}'
```

#### update
```
gws drive revisions update --params '{"fileId": "<FILE_ID>", "revisionId": "<REVISION_ID>"}' \
  --json '{"keepForever": true}'
```

#### delete
```
gws drive revisions delete --params '{"fileId": "<FILE_ID>", "revisionId": "<REVISION_ID>"}'
```

### drives (Shared Drives)

#### list
```
gws drive drives list
gws drive drives list --params '{"pageSize": 50}'
```

#### get
```
gws drive drives get --params '{"driveId": "<DRIVE_ID>"}'
```

#### create
Provide a unique `requestId` in `--params`.

```
gws drive drives create --params '{"requestId": "unique-id-123"}' --json '{"name": "Engineering Drive"}'
```

#### update
```
gws drive drives update --params '{"driveId": "<DRIVE_ID>"}' --json '{"name": "Renamed Drive"}'
```

#### delete
```
gws drive drives delete --params '{"driveId": "<DRIVE_ID>"}'
```

---

## Sheets

### spreadsheets

#### create
Create a new spreadsheet.

```
gws sheets spreadsheets create --json '{"properties": {"title": "My Spreadsheet"}}'
```

#### get
Get spreadsheet metadata (sheets, named ranges, etc.).

```
gws sheets spreadsheets get --params '{"spreadsheetId": "<SPREADSHEET_ID>"}'
gws sheets spreadsheets get --params '{"spreadsheetId": "<SPREADSHEET_ID>", "fields": "spreadsheetId,properties.title,sheets.properties"}'
```

#### batchUpdate
Apply one or more structural changes (add/delete sheets, merge cells, formatting, charts, pivot tables, etc.).

```
gws sheets spreadsheets batchUpdate --params '{"spreadsheetId": "<SPREADSHEET_ID>"}' --json '{
  "requests": [
    {"addSheet": {"properties": {"title": "New Tab"}}},
    {"deleteSheet": {"sheetId": 0}}
  ]
}'
```

### spreadsheets values

> Note: these live under `sheets spreadsheets values`, **not** `sheets values`.

#### get
Read a range of cell values.

```
gws sheets spreadsheets values get --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Sheet1!A1:D10"}'
gws sheets spreadsheets values get --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Sheet1!A1:D10", "valueRenderOption": "FORMATTED_VALUE"}'
```

#### update
Write values to a range. Set `valueInputOption` to `USER_ENTERED` (applies formulas/formatting) or `RAW` (stores literal strings).

```
gws sheets spreadsheets values update \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Sheet1!A1", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["Name", "Score"], ["Alice", 95], ["Bob", 87]]}'
```

#### append
Append rows after the last row with data in the given range.

```
gws sheets spreadsheets values append \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Sheet1!A:D", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["Charlie", 92], ["Diana", 88]]}'
```

#### clear
Clear values from a range (preserves formatting).

```
gws sheets spreadsheets values clear --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Sheet1!A1:D10"}'
```

#### batchGet
Read multiple ranges in one call.

```
gws sheets spreadsheets values batchGet \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>", "ranges": ["Sheet1!A1:B5", "Sheet2!A1:C3"]}'
```

#### batchUpdate
Write to multiple ranges in one call.

```
gws sheets spreadsheets values batchUpdate --params '{"spreadsheetId": "<SPREADSHEET_ID>"}' --json '{
  "valueInputOption": "USER_ENTERED",
  "data": [
    {"range": "Sheet1!A1", "values": [["Header1", "Header2"]]},
    {"range": "Sheet2!A1", "values": [["Data1", "Data2"]]}
  ]
}'
```

### spreadsheets sheets

#### copyTo
Copy a sheet to another spreadsheet.

```
gws sheets spreadsheets sheets copyTo \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>", "sheetId": <SHEET_ID_INT>}' \
  --json '{"destinationSpreadsheetId": "<TARGET_SPREADSHEET_ID>"}'
```

---

## Docs

### documents

#### create
Create a new Google Doc.

```
gws docs documents create --json '{"title": "My Document"}'
```

#### get
Retrieve document content and metadata.

```
gws docs documents get --params '{"documentId": "<DOCUMENT_ID>"}'
```

#### batchUpdate
Apply structural edits: insert/delete text, apply formatting, insert tables, images, page breaks, etc.

```
gws docs documents batchUpdate --params '{"documentId": "<DOCUMENT_ID>"}' --json '{
  "requests": [
    {"insertText": {"location": {"index": 1}, "text": "Hello, World!\n"}},
    {"updateTextStyle": {
      "range": {"startIndex": 1, "endIndex": 14},
      "textStyle": {"bold": true, "fontSize": {"magnitude": 18, "unit": "PT"}},
      "fields": "bold,fontSize"
    }}
  ]
}'
```

---

## Slides

### presentations

#### create
Create a new presentation.

```
gws slides presentations create --json '{"title": "My Presentation"}'
```

#### get
Retrieve presentation metadata and slide content.

```
gws slides presentations get --params '{"presentationId": "<PRESENTATION_ID>"}'
```

#### batchUpdate
Apply changes: create slides, insert text, add images, update layouts, etc.

```
gws slides presentations batchUpdate --params '{"presentationId": "<PRESENTATION_ID>"}' --json '{
  "requests": [
    {"createSlide": {"insertionIndex": 1, "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"}}}
  ]
}'
```

### presentations pages

#### get
Get a specific page (slide, layout, or master).

```
gws slides presentations pages get --params '{"presentationId": "<PRESENTATION_ID>", "pageObjectId": "<PAGE_ID>"}'
```

#### getThumbnail
Get a thumbnail image of a page. Save with `--output`.

```
gws slides presentations pages getThumbnail \
  --params '{"presentationId": "<PRESENTATION_ID>", "pageObjectId": "<PAGE_ID>", "thumbnailProperties.mimeType": "PNG", "thumbnailProperties.thumbnailSize": "LARGE"}' \
  --output /tmp/slide-thumb.png
```

---

## Gmail

> All Gmail API commands live under `gws gmail users <resource> <method>` and need `"userId": "me"` in `--params`.

### users messages

#### list
List messages matching a query.

```
gws gmail users messages list --params '{"userId": "me", "q": "is:unread", "maxResults": 20}'
gws gmail users messages list --params '{"userId": "me", "q": "from:boss@example.com newer_than:7d"}' --page-all
```

#### get
Get a specific message. Use `format` param: `full`, `metadata`, `minimal`, `raw`.

```
gws gmail users messages get --params '{"userId": "me", "id": "<MESSAGE_ID>"}'
gws gmail users messages get --params '{"userId": "me", "id": "<MESSAGE_ID>", "format": "full"}'
gws gmail users messages get --params '{"userId": "me", "id": "<MESSAGE_ID>", "format": "raw"}' --output /tmp/email.eml
```

#### send
Send an email. Provide the RFC 2822 message as a base64url-encoded `raw` field. For most cases, prefer `gws gmail +send`.

```
gws gmail users messages send --params '{"userId": "me"}' --json '{"raw": "<BASE64URL_ENCODED_RFC2822>"}'
```

#### trash
```
gws gmail users messages trash --params '{"userId": "me", "id": "<MESSAGE_ID>"}'
```

#### untrash
```
gws gmail users messages untrash --params '{"userId": "me", "id": "<MESSAGE_ID>"}'
```

#### delete
Permanently delete a message (irreversible).

```
gws gmail users messages delete --params '{"userId": "me", "id": "<MESSAGE_ID>"}'
```

#### modify
Add or remove labels on a message.

```
gws gmail users messages modify --params '{"userId": "me", "id": "<MESSAGE_ID>"}' \
  --json '{"addLabelIds": ["UNREAD"], "removeLabelIds": ["INBOX"]}'
```

#### batchModify
Modify labels on multiple messages at once.

```
gws gmail users messages batchModify --params '{"userId": "me"}' --json '{
  "ids": ["<MSG_ID_1>", "<MSG_ID_2>"],
  "addLabelIds": ["Label_123"],
  "removeLabelIds": ["UNREAD"]
}'
```

### users drafts

> Drafts use the path parameter name `id`, not `draftId`.

#### list
```
gws gmail users drafts list --params '{"userId": "me"}'
```

#### get
```
gws gmail users drafts get --params '{"userId": "me", "id": "<DRAFT_ID>"}'
```

#### create
```
gws gmail users drafts create --params '{"userId": "me"}' \
  --json '{"message": {"raw": "<BASE64URL_ENCODED_RFC2822>"}}'
```

#### update
```
gws gmail users drafts update --params '{"userId": "me", "id": "<DRAFT_ID>"}' \
  --json '{"message": {"raw": "<BASE64URL_ENCODED_RFC2822>"}}'
```

#### send
```
gws gmail users drafts send --params '{"userId": "me"}' --json '{"id": "<DRAFT_ID>"}'
```

#### delete
```
gws gmail users drafts delete --params '{"userId": "me", "id": "<DRAFT_ID>"}'
```

### users labels

> Labels use the path parameter name `id`, not `labelId`.

#### list
```
gws gmail users labels list --params '{"userId": "me"}'
```

#### get
```
gws gmail users labels get --params '{"userId": "me", "id": "<LABEL_ID>"}'
```

#### create
```
gws gmail users labels create --params '{"userId": "me"}' \
  --json '{"name": "Projects/Active", "labelListVisibility": "labelShow", "messageListVisibility": "show"}'
```

#### update
```
gws gmail users labels update --params '{"userId": "me", "id": "<LABEL_ID>"}' \
  --json '{"name": "Projects/Archive"}'
```

#### delete
```
gws gmail users labels delete --params '{"userId": "me", "id": "<LABEL_ID>"}'
```

### users threads

> Threads use the path parameter name `id`, not `threadId`.

#### list
```
gws gmail users threads list --params '{"userId": "me", "q": "subject:weekly report"}'
```

#### get
```
gws gmail users threads get --params '{"userId": "me", "id": "<THREAD_ID>"}'
```

#### modify
```
gws gmail users threads modify --params '{"userId": "me", "id": "<THREAD_ID>"}' \
  --json '{"addLabelIds": ["IMPORTANT"]}'
```

#### trash
```
gws gmail users threads trash --params '{"userId": "me", "id": "<THREAD_ID>"}'
```

#### untrash
```
gws gmail users threads untrash --params '{"userId": "me", "id": "<THREAD_ID>"}'
```

#### delete
```
gws gmail users threads delete --params '{"userId": "me", "id": "<THREAD_ID>"}'
```

### users history

#### list
List history of changes since a given `startHistoryId`.

```
gws gmail users history list \
  --params '{"userId": "me", "startHistoryId": "12345", "historyTypes": ["messageAdded", "labelAdded"]}'
```

### Gmail Search Operators

Use these in the `q` parameter for `users messages list` and `users threads list`.

| Operator | Description |
|----------|-------------|
| `from:sender@example.com` | Messages from a specific sender |
| `to:recipient@example.com` | Messages to a specific recipient |
| `subject:keyword` | Messages with keyword in subject |
| `has:attachment` | Messages with attachments |
| `is:unread` | Unread messages |
| `is:read` | Read messages |
| `is:starred` | Starred messages |
| `newer_than:7d` | Messages newer than 7 days (`d`, `m`, `y`) |
| `older_than:30d` | Messages older than 30 days |
| `after:2025/01/01` | Messages after a date (YYYY/MM/DD) |
| `before:2025/12/31` | Messages before a date |
| `label:projects` | Messages with a specific label |
| `filename:pdf` | Messages with attachment filename matching |
| `larger:5M` | Messages larger than 5 MB |
| `smaller:1M` | Messages smaller than 1 MB |
| `"exact phrase"` | Messages containing an exact phrase |
| `in:inbox` | Messages in inbox |
| `in:sent` | Messages in sent mail |
| `in:trash` | Messages in trash |
| `in:anywhere` | Messages in all folders including spam/trash |
| `category:primary` | Messages in Primary category |
| `category:social` | Messages in Social category |
| `category:promotions` | Messages in Promotions category |
| `category:updates` | Messages in Updates category |
| `category:forums` | Messages in Forums category |

Combine operators with spaces (implicit AND) or `OR`:
```
from:alice@example.com subject:invoice newer_than:30d
from:alice@example.com OR from:bob@example.com has:attachment
```

---

## Calendar

### events

#### list
List events on a calendar. Default calendar: `primary`.

```
gws calendar events list --params '{"calendarId": "<CALENDAR_ID>", "timeMin": "2025-01-01T00:00:00Z", "timeMax": "2025-12-31T23:59:59Z", "singleEvents": true, "orderBy": "startTime"}'
gws calendar events list --params '{"calendarId": "primary", "timeMin": "2025-04-01T00:00:00Z", "maxResults": 10, "singleEvents": true}'
```

#### get
```
gws calendar events get --params '{"calendarId": "<CALENDAR_ID>", "eventId": "<EVENT_ID>"}'
```

#### insert
Create a new event.

```
gws calendar events insert --params '{"calendarId": "<CALENDAR_ID>"}' --json '{
  "summary": "Team Standup",
  "location": "Conference Room A",
  "description": "Daily sync meeting",
  "start": {"dateTime": "2025-04-10T09:00:00+05:30", "timeZone": "Asia/Kolkata"},
  "end": {"dateTime": "2025-04-10T09:30:00+05:30", "timeZone": "Asia/Kolkata"},
  "attendees": [
    {"email": "alice@example.com"},
    {"email": "bob@example.com"}
  ],
  "reminders": {"useDefault": false, "overrides": [{"method": "popup", "minutes": 10}]}
}'
```

#### update
Update an existing event.

```
gws calendar events update --params '{"calendarId": "<CALENDAR_ID>", "eventId": "<EVENT_ID>"}' \
  --json '{"summary": "Updated Meeting Title"}'
```

#### delete
```
gws calendar events delete --params '{"calendarId": "<CALENDAR_ID>", "eventId": "<EVENT_ID>"}'
```

#### quickAdd
Create an event from a natural-language string.

```
gws calendar events quickAdd \
  --params '{"calendarId": "<CALENDAR_ID>", "text": "Lunch with Alice at noon tomorrow at Cafe Mocha"}'
```

#### instances
List instances of a recurring event.

```
gws calendar events instances \
  --params '{"calendarId": "<CALENDAR_ID>", "eventId": "<EVENT_ID>", "timeMin": "2025-04-01T00:00:00Z", "timeMax": "2025-06-30T23:59:59Z"}'
```

#### move
Move an event to a different calendar. `destination` is required.

```
gws calendar events move \
  --params '{"calendarId": "<CALENDAR_ID>", "eventId": "<EVENT_ID>", "destination": "<TARGET_CALENDAR_ID>"}'
```

#### watch
Set up push notifications for event changes.

```
gws calendar events watch --params '{"calendarId": "<CALENDAR_ID>"}' \
  --json '{"id": "unique-channel-id", "type": "web_hook", "address": "https://example.com/webhook"}'
```

### calendarList

#### list
List all calendars on the user's calendar list.

```
gws calendar calendarList list
```

#### get
```
gws calendar calendarList get --params '{"calendarId": "<CALENDAR_ID>"}'
```

#### insert
Add an existing calendar to the user's list.

```
gws calendar calendarList insert --json '{"id": "shared-calendar@group.calendar.google.com"}'
```

#### update
```
gws calendar calendarList update --params '{"calendarId": "<CALENDAR_ID>"}' \
  --json '{"colorId": "9", "selected": true}'
```

#### delete
Remove a calendar from the user's list.

```
gws calendar calendarList delete --params '{"calendarId": "<CALENDAR_ID>"}'
```

### settings

#### list
```
gws calendar settings list
```

#### get
> Uses path param name `setting` (not `settingId`).

```
gws calendar settings get --params '{"setting": "<SETTING_ID>"}'
```

### freebusy

#### query
Query free/busy information for one or more calendars.

```
gws calendar freebusy query --json '{
  "timeMin": "2025-04-10T00:00:00Z",
  "timeMax": "2025-04-10T23:59:59Z",
  "items": [{"id": "primary"}, {"id": "alice@example.com"}]
}'
```

---

## Tasks

> Tasks uses path param names **`tasklist`** and **`task`** (not `tasklistId` / `taskId`).

### tasklists

#### list
```
gws tasks tasklists list
```

#### get
```
gws tasks tasklists get --params '{"tasklist": "<TASKLIST_ID>"}'
```

#### insert
```
gws tasks tasklists insert --json '{"title": "Work Tasks"}'
```

#### update
```
gws tasks tasklists update --params '{"tasklist": "<TASKLIST_ID>"}' --json '{"title": "Renamed Task List"}'
```

#### delete
```
gws tasks tasklists delete --params '{"tasklist": "<TASKLIST_ID>"}'
```

### tasks

#### list
```
gws tasks tasks list --params '{"tasklist": "<TASKLIST_ID>"}'
gws tasks tasks list --params '{"tasklist": "<TASKLIST_ID>", "showCompleted": false, "showHidden": false}'
```

#### get
```
gws tasks tasks get --params '{"tasklist": "<TASKLIST_ID>", "task": "<TASK_ID>"}'
```

#### insert
```
gws tasks tasks insert --params '{"tasklist": "<TASKLIST_ID>"}' \
  --json '{"title": "Review PR #42", "notes": "Check edge cases", "due": "2025-04-15T00:00:00Z"}'
```

#### update
```
gws tasks tasks update --params '{"tasklist": "<TASKLIST_ID>", "task": "<TASK_ID>"}' \
  --json '{"title": "Updated task title", "status": "completed"}'
```

#### delete
```
gws tasks tasks delete --params '{"tasklist": "<TASKLIST_ID>", "task": "<TASK_ID>"}'
```

#### move
Reorder a task or move it under a parent task.

```
gws tasks tasks move \
  --params '{"tasklist": "<TASKLIST_ID>", "task": "<TASK_ID>", "parent": "<PARENT_TASK_ID>", "previous": "<PREVIOUS_TASK_ID>"}'
```

#### clear
Remove all completed tasks from a task list.

```
gws tasks tasks clear --params '{"tasklist": "<TASKLIST_ID>"}'
```

---

## Common MIME Types

### Google Native Formats

| Format | MIME Type |
|--------|-----------|
| Google Doc | `application/vnd.google-apps.document` |
| Google Sheet | `application/vnd.google-apps.spreadsheet` |
| Google Slides | `application/vnd.google-apps.presentation` |
| Google Drawing | `application/vnd.google-apps.drawing` |
| Google Form | `application/vnd.google-apps.form` |
| Google Script | `application/vnd.google-apps.script` |
| Google Site | `application/vnd.google-apps.site` |
| Google Shortcut | `application/vnd.google-apps.shortcut` |
| Folder | `application/vnd.google-apps.folder` |

### Export MIME Types (for `files export`)

| Target Format | MIME Type |
|---------------|-----------|
| PDF | `application/pdf` |
| Plain text | `text/plain` |
| Rich text (RTF) | `application/rtf` |
| HTML | `text/html` |
| CSV | `text/csv` |
| TSV | `text/tab-separated-values` |
| DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| XLSX | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| PPTX | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |
| EPUB | `application/epub+zip` |
| Open Document Text | `application/vnd.oasis.opendocument.text` |
| Open Document Sheet | `application/vnd.oasis.opendocument.spreadsheet` |
| Open Document Presentation | `application/vnd.oasis.opendocument.presentation` |
| PNG (Drawings) | `image/png` |
| JPEG (Drawings) | `image/jpeg` |
| SVG (Drawings) | `image/svg+xml` |

### Upload MIME Types (for `files create` / `files update`)

| File Type | MIME Type |
|-----------|-----------|
| PDF | `application/pdf` |
| DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| XLSX | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| PPTX | `application/vnd.openxmlformats-officedocument.presentationml.presentation` |
| CSV | `text/csv` |
| Plain text | `text/plain` |
| HTML | `text/html` |
| JSON | `application/json` |
| PNG | `image/png` |
| JPEG | `image/jpeg` |
| GIF | `image/gif` |
| SVG | `image/svg+xml` |
| MP4 | `video/mp4` |
| MP3 | `audio/mpeg` |
| WAV | `audio/wav` |
| ZIP | `application/zip` |

---

## Sharing Patterns

### Share with anyone (public link)

```
gws drive permissions create --params '{"fileId": "<FILE_ID>"}' \
  --json '{"role": "reader", "type": "anyone"}'
```

Retrieve the shareable link after granting permission:
```
gws drive files get --params '{"fileId": "<FILE_ID>", "fields": "webViewLink"}'
```

### Share with a specific user

```
# Read-only
gws drive permissions create --params '{"fileId": "<FILE_ID>"}' \
  --json '{"role": "reader", "type": "user", "emailAddress": "user@example.com"}'

# Edit access
gws drive permissions create --params '{"fileId": "<FILE_ID>"}' \
  --json '{"role": "writer", "type": "user", "emailAddress": "user@example.com"}'

# Comment-only
gws drive permissions create --params '{"fileId": "<FILE_ID>"}' \
  --json '{"role": "commenter", "type": "user", "emailAddress": "user@example.com"}'
```

### Share with a domain

```
gws drive permissions create --params '{"fileId": "<FILE_ID>"}' \
  --json '{"role": "reader", "type": "domain", "domain": "example.com"}'
```

### Share with a Google Group

```
gws drive permissions create --params '{"fileId": "<FILE_ID>"}' \
  --json '{"role": "writer", "type": "group", "emailAddress": "team@googlegroups.com"}'
```

### Transfer ownership

```
gws drive permissions create \
  --params '{"fileId": "<FILE_ID>", "transferOwnership": true}' \
  --json '{"role": "owner", "type": "user", "emailAddress": "newowner@example.com"}'
```
