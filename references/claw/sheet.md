# `claw sheet` — Google Sheets / Drive Reference

CLI wrapper over Google Sheets and Drive APIs (via `gws`).

## Contents

- **CREATE / UPLOAD**
  - [Upload file](#11-upload) · [Copy file](#12-copy)
- **READ / DOWNLOAD**
  - [Download to XLSX](#21-download) · [List files](#22-list)
- **EDIT / MANAGE**
  - [Move file](#31-move) · [Rename file](#32-rename) · [Delete file](#33-delete)
- **SHARE**
  - [List permissions](#41-share-list) · [Revoke access](#42-share-revoke)

---

## Critical Rules

1. **ID vs Path** — Use `DOC_ID` for existing files and standard local paths for uploads/downloads.
2. **Safe Deletes** — `delete` is permanent in Drive (does not use Trash). Use with caution.
3. **Conversion** — `--convert` on upload is required to turn a local `.xlsx` into a Google Sheet.
4. **Auth** — Depends on `gws auth login` being completed first.

---

## 1.1 upload
Upload a local file to Drive.
```bash
claw sheet upload <LOCAL_FILE> [--name <DRIVE_NAME>] [--convert] [--parent <FOLDER_ID>] [--force]
```

## 1.2 copy
Duplicate a file in Drive.
```bash
claw sheet copy <FILE_ID> [--name <NEW_NAME>] [--json]
```

---

## 2.1 download
Download a Google Sheet as a local `.xlsx`.
```bash
claw sheet download <FILE_ID> <OUT_XLSX> [--force]
```

## 2.2 list
List files in Drive.
```bash
claw sheet list [--query <Q>] [--json]
```

---

## 3.1 move
Move a file to a different folder.
```bash
claw sheet move <FILE_ID> --to <FOLDER_ID> [--json]
```

## 3.2 rename
Rename a file in Drive.
```bash
claw sheet rename <FILE_ID> --name <NEW_NAME> [--json]
```

## 3.3 delete
Permanently delete a file.
```bash
claw sheet delete <FILE_ID> [--force]
```

---

## 4.1 share-list
List all permissions (emails and roles) for a file.
```bash
claw sheet share-list <FILE_ID> [--json]
```

## 4.2 share-revoke
Remove a user's access.
```bash
claw sheet share-revoke <FILE_ID> --email <USER_EMAIL> [--json]
```

---

## Footguns
- **No Trash** — `claw sheet delete` bypasses the Trash folder.
- **Conversion** — If you forget `--convert`, the `.xlsx` is uploaded as a binary blob, not a spreadsheet.

## Escape Hatch
- [gws CLI reference](../gws-cli.md#sheets) — Full access to sharing, advanced queries, and metadata.

---

## Quick Reference
| Task | Command |
|------|---------|
| Upload & Convert | `claw sheet upload data.xlsx --convert` |
| Download to Local | `claw sheet download FILE_ID report.xlsx` |
| List Drive Files | `claw sheet list --json` |
| Delete File | `claw sheet delete FILE_ID --force` |
