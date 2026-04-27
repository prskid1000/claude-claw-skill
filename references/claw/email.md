# `claw email` — Gmail / Email Reference

CLI wrapper over Gmail API (via `gws`) and standard MIME generation.

## Contents

- **COMPOSE / SEND**
  - [Send email](#11-send) · [Draft email](#12-draft)
- **RESPOND**
  - [Reply](#21-reply) · [Forward](#22-forward)
- **MANAGE**
  - [Search](#31-search) · [Download attachment](#32-download-attachment)

---

## Critical Rules

1. **Dry Run First** — Use `--dry-run` to preview the generated MIME and recipient list without sending.
2. **Auth** — Primary mode requires `gws auth login` with Gmail scopes enabled.
3. **Attachments** — Use `--attach <PATH>` for standard files; use `--inline CID=<PATH>` for images referenced in HTML.

---

## 1.1 send
Compose and send an email immediately. `--to` is repeatable; body comes from one of `--body`/`--body-file`/`--body-stdin`; HTML alternative via `--html`.
```bash
claw email send --to <EMAIL> --subject <TEXT> [--body <TEXT> | --body-file <FILE> | --body-stdin] [--html <FILE>] [--cc <EMAIL>] [--bcc <EMAIL>] [--attach @<PATH>[:mime/type]] [--inline CID=@<PATH>] [--from <EMAIL>] [--reply-to <EMAIL>] [--header KEY=VAL]
```

## 1.2 draft
Create an email draft in the user's Gmail account (same option surface as `send`).
```bash
claw email draft --to <EMAIL> --subject <TEXT> [--body <TEXT> | --body-file <FILE> | --body-stdin] [--html <FILE>] [--cc <EMAIL>] [--bcc <EMAIL>] [--attach @<PATH>] [--inline CID=@<PATH>] [--from <EMAIL>] [--reply-to <EMAIL>] [--header KEY=VAL]
```

---

## 2.1 reply
Reply to an existing message (auto-populates In-Reply-To/References).
```bash
claw email reply <MSG_ID> [--body <TEXT> | --body-file <FILE> | --body-stdin] [--all] [--remove <EMAIL>] [--add-cc <EMAIL>] [--html <FILE>] [--attach @<PATH>] [--inline CID=@<PATH>] [--subject <TEXT>]
```

## 2.2 forward
Forward a message to new recipients with an optional note.
```bash
claw email forward <MSG_ID> --to <EMAIL> [--cc <EMAIL>] [--bcc <EMAIL>] [--body <TEXT> | --body-file <FILE> | --body-stdin] [--subject <TEXT>] [--no-attachments] [--strip-html] [--attach @<PATH>]
```

---

## 3.1 search
Search Gmail messages using standard Gmail query syntax.
```bash
claw email search --q <QUERY> [--max N] [--format table|json|full] [--include-spam-trash] [--label <LABEL>]
```

## 3.2 download-attachment
Save an attachment from a specific message to disk; optionally verify SHA-256.
```bash
claw email download-attachment <MSG_ID> <ATT_ID> --out <PATH> [--verify-hash <SHA256>]
```

---

## Footguns
- **Gmail Scopes** — If `claw doctor` reports scope errors, you must re-auth with `gws auth login`.
- **Large Attachments** — Standard Gmail API limit is 25MB including base64 encoding overhead.

## Escape Hatch
- [gws CLI reference](../gws-cli.md#gmail) · [Python email.mime docs](https://docs.python.org/3/library/email.mime.html)

---

## Quick Reference
| Task | Command |
|------|---------|
| Send HTML Report | `claw email send --to x@y.z --subject "Q3" --html report.html` |
| Draft Reply | `claw email reply MSG_ID --body "Got it" --dry-run` |
| Search PDF bills | `claw email search --q "filename:pdf bill" --json` |
| Download Invoice | `claw email download-attachment MSG_ID ATT_ID --out inv.pdf` |
