# Obsidian CLI — Practical Command Reference

> Built-in CLI for Obsidian (v1.12+). Remote-controls a running Obsidian instance.

**Related:** [examples/obsidian-workflows.md](../examples/obsidian-workflows.md) | [setup.md](setup.md)

---

## Setup

1. Install Obsidian v1.12+ (already adds `obsidian` to PATH on Windows)
2. Enable in **Settings > General > Command line interface**
3. Obsidian must be running (auto-launches on first command)
4. Verify: `obsidian version`

If `obsidian` not found on Windows:
```bash
export PATH="$PATH:/c/Users/prith/AppData/Local/Obsidian"
```

## Syntax Rules

```bash
obsidian <command> [params] [flags]
```

- **Parameters**: `key="value"` — quotes required for values with spaces
- **Flags**: boolean, no value — `silent`, `overwrite`, `--copy`, `total`
- **Multiline content**: `\n` for newlines, `\t` for tabs
- **File targeting**: `file="Name"` (wikilink-style, no path/ext) or `path="folder/note.md"` (exact)
- **Vault targeting**: `vault="My Vault"` as first param (defaults to most recent)
- **Output**: `--copy` = clipboard, `format=json` = JSON output, `total` = count only
- **TUI mode**: `obsidian` with no args = interactive terminal with autocomplete

---

## Note CRUD

### `read` — Read note content

```bash
obsidian read                           # active file
obsidian read file="Project Plan"       # by wikilink name
obsidian read path="projects/plan.md"   # by exact path
obsidian read file="Note" --copy        # copy to clipboard
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | string | active file | Wikilink-style name (no path/extension) |
| `path` | string | — | Exact path from vault root (e.g., `folder/note.md`) |
| `--copy` | flag | — | Copy output to clipboard |

### `create` — Create a new note

```bash
obsidian create name="Meeting Notes" content="# Meeting\n\n## Agenda"
obsidian create name="Weekly Review" template="Weekly Template" silent
obsidian create name="Existing Note" content="Replaced" overwrite
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | **required** | Note name (created in vault root unless path included) |
| `content` | string | — | Note body (`\n` for newlines, `\t` for tabs) |
| `template` | string | — | Template name to use |
| `silent` | flag | — | Don't open the note after creation |
| `overwrite` | flag | — | Overwrite if note already exists |

### `append` — Append content to end of note

```bash
obsidian append file="Log" content="\n- New entry"
obsidian append content="Added to active file"
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | string | active file | Target note |
| `content` | string | **required** | Content to append |

### `prepend` — Prepend content after frontmatter

```bash
obsidian prepend file="Inbox" content="- [ ] Urgent task"
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | string | active file | Target note |
| `content` | string | **required** | Content to prepend (inserted after YAML frontmatter) |

### `move` — Move or rename file

```bash
obsidian move file="Draft" to="archive/Draft"
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | string | active file | Source note |
| `to` | string | **required** | Destination path (from vault root) |

### `delete` — Delete note to trash

```bash
obsidian delete file="Scratch"
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | string | active file | Note to delete (moved to trash, recoverable) |

---

## Daily Notes

### `daily` — Open today's daily note

```bash
obsidian daily                    # open in editor
```

### `daily:read` — Read daily note content

```bash
obsidian daily:read               # stdout
obsidian daily:read --copy        # to clipboard
```

### `daily:append` — Add to end of daily note

```bash
obsidian daily:append content="- [ ] Review PRs"
obsidian daily:append content="## Meeting Notes\n- Discussed roadmap\n- Action: update board"
```

| Param | Type | Description |
|-------|------|-------------|
| `content` | string | Content to append (`\n` for newlines) |

### `daily:prepend` — Add after frontmatter of daily note

```bash
obsidian daily:prepend content="## Priority\n- Ship feature X"
```

### `daily:path` — Get daily note file path

```bash
obsidian daily:path               # returns e.g., "Daily/2026-04-04.md"
```

---

## Search

### `search` — Search vault by query

```bash
obsidian search query="deployment"
obsidian search query="API endpoint" limit=10
obsidian search query="deployment" format=json
obsidian search query="tag:#urgent" limit=5
obsidian search query="task-todo:" limit=20
obsidian search query="path:projects/ meeting" --copy
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | **required** | Search query (supports operators — see below) |
| `limit` | int | all | Max results to return |
| `format` | string | text | Output format: `json` for structured data |
| `--copy` | flag | — | Copy results to clipboard |

### `search:context` — Search with surrounding lines (grep-style)

```bash
obsidian search:context query="TODO" limit=10
```

### Search Operators (use inside `query=`)

| Operator | Example | Purpose |
|----------|---------|---------|
| `file:` | `file:meeting` | Filter by filename |
| `path:` | `path:projects/` | Filter by folder path |
| `content:` | `content:TODO` | Search in body only (not filename) |
| `tag:` | `tag:#important` | Filter by tag |
| `task:` | `task:` | Find all tasks |
| `task-todo:` | `task-todo:` | Find incomplete tasks |
| `task-done:` | `task-done:` | Find completed tasks |
| `line:` | `line:(foo bar)` | Both terms on same line |
| `section:` | `section:(heading text)` | Within a heading section |

---

## Tasks

### `tasks` — List tasks from vault

```bash
obsidian tasks                    # all tasks
obsidian tasks todo               # incomplete only
obsidian tasks done               # completed only
obsidian tasks daily              # from today's daily note
obsidian tasks daily todo         # incomplete from daily note
obsidian tasks file="Sprint" todo limit=10
obsidian tasks todo total         # just the count
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `file` | string | all files | Filter to specific note |
| `limit` | int | all | Max tasks to return |
| `todo` | flag | — | Incomplete tasks only |
| `done` | flag | — | Completed tasks only |
| `daily` | flag | — | From today's daily note only |
| `total` | flag | — | Return count instead of list |

---

## Tags & Properties

### `tags` — List all vault tags

```bash
obsidian tags                     # list all
obsidian tags counts              # with occurrence counts
obsidian tags counts sort=count   # sorted by frequency
obsidian tags sort=name           # sorted alphabetically
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `sort` | string | name | Sort by: `count` or `name` |
| `counts` | flag | — | Show occurrence count per tag |

### `property:read` — Read frontmatter property

```bash
obsidian property:read name="status" file="Feature Spec"
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | **required** | Property name |
| `file` | string | active file | Target note |

### `property:set` — Set frontmatter property

```bash
obsidian property:set name="status" value="done" file="Feature Spec"
obsidian property:set name="priority" value="high" file="Bug Report"
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | **required** | Property name |
| `value` | string | **required** | Property value |
| `file` | string | active file | Target note |

### `property:remove` — Remove frontmatter property

```bash
obsidian property:remove name="draft" file="Published Article"
```

---

## Files & Discovery

### `files` — List vault files

```bash
obsidian files                           # all files
obsidian files sort=modified limit=10    # 10 most recently modified
obsidian files sort=created limit=5      # 5 newest files
obsidian files sort=name --copy          # alphabetical, to clipboard
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `sort` | string | name | Sort by: `modified`, `created`, `name` |
| `limit` | int | all | Max files to return |
| `--copy` | flag | — | Copy to clipboard |

### `backlinks` — List incoming links to a note

```bash
obsidian backlinks file="Project Plan"
```

### `links` — List outgoing links from a note

```bash
obsidian links file="Project Plan"
```

### `unresolved` — Find broken/unresolved links

```bash
obsidian unresolved
```

### `outline` — Show heading structure

```bash
obsidian outline file="Architecture Doc"
```

### `wordcount` — Count words/characters

```bash
obsidian wordcount file="Blog Post"
```

---

## Templates

### `templates` — List available templates

```bash
obsidian templates
```

### `template:insert` — Insert template into active file

```bash
obsidian template:insert name="Meeting Notes"
```

| Param | Type | Description |
|-------|------|-------------|
| `name` | string | Template name to insert |

---

## Workspaces

### `workspace:save` / `workspace:load` — Save and restore layouts

```bash
obsidian workspace:save name="coding-layout"
obsidian workspace:load name="writing-layout"
obsidian workspaces                      # list saved workspaces
```

| Param | Type | Description |
|-------|------|-------------|
| `name` | string | Workspace name |

---

## Plugins

### `plugin:reload` — Reload plugin (development)

```bash
obsidian plugin:reload id="my-plugin"
```

### `plugins` — List installed plugins

```bash
obsidian plugins                  # all installed
obsidian plugins:enabled          # enabled only
```

### `plugin:install` / `plugin:enable` / `plugin:disable`

```bash
obsidian plugin:install id="dataview"
obsidian plugin:enable id="calendar"
obsidian plugin:disable id="calendar"
```

| Param | Type | Description |
|-------|------|-------------|
| `id` | string | Plugin ID (from community plugins) |

---

## Developer & Debugging

### `dev:screenshot` — Take screenshot of Obsidian window

```bash
obsidian dev:screenshot path="/tmp/screenshot.png"
obsidian dev:screenshot path="C:/Users/prith/Desktop/obsidian.png"
```

| Param | Type | Description |
|-------|------|-------------|
| `path` | string | Output file path for PNG |

### `eval` — Execute JavaScript in Obsidian

```bash
obsidian eval code="app.vault.getFiles().length"
obsidian eval code="app.vault.getName()"
obsidian eval code="app.workspace.getActiveFile()?.path"
obsidian eval code="app.vault.getMarkdownFiles().map(f => f.path).join('\n')"
```

| Param | Type | Description |
|-------|------|-------------|
| `code` | string | JavaScript to execute (has access to Obsidian `app` API) |

### `dev:errors` — Show JavaScript errors

```bash
obsidian dev:errors
```

### `dev:console` — Show console messages by level

```bash
obsidian dev:console level=error
obsidian dev:console level=warn
```

| Param | Type | Description |
|-------|------|-------------|
| `level` | string | Filter: `error`, `warn`, `log`, `debug` |

### `dev:dom` — Query DOM elements

```bash
obsidian dev:dom selector=".workspace-leaf"
obsidian dev:dom selector=".nav-file-title" text
```

| Param | Type | Description |
|-------|------|-------------|
| `selector` | string | CSS selector |
| `text` | flag | Return text content only |

### `dev:css` — Inspect computed CSS

```bash
obsidian dev:css selector=".workspace-leaf" prop=background-color
```

| Param | Type | Description |
|-------|------|-------------|
| `selector` | string | CSS selector |
| `prop` | string | CSS property to inspect |

---

## Sync (if using Obsidian Sync)

```bash
obsidian sync:status              # show sync status and usage
obsidian sync pause               # pause sync
obsidian sync resume              # resume sync
```

---

## Multi-Vault

Target a specific vault by adding `vault=` as the first parameter:

```bash
obsidian vault="Work" search query="meeting"
obsidian vault="Personal" daily:read
obsidian vaults                   # list all known vaults
```
