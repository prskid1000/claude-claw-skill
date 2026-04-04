# Obsidian CLI — Complete Command Reference

> Built-in CLI for Obsidian (v1.12+). Remote-controls a running Obsidian instance from the terminal.

**Related:** [examples/obsidian-workflows.md](../examples/obsidian-workflows.md) | [setup.md](setup.md)

---

## Setup

Enable in **Settings > General > Command line interface**. Obsidian must be running (auto-launches on first command). Run `obsidian help` for the latest command list.

## Syntax Rules

- **Parameters**: `key="value"` — use `=` with quotes for values containing spaces
- **Flags**: boolean switches, no value — e.g., `silent`, `overwrite`, `--copy`
- **Multiline**: `\n` for newlines, `\t` for tabs in content strings
- **File targeting**: `file="Name"` (wikilink-style) or `path="folder/note.md"` (exact path)
- **Vault targeting**: `vault="My Vault"` as first parameter (defaults to most recently focused)
- **Output**: `--copy` copies to clipboard, `format=json` for JSON output, `total` for counts
- **TUI mode**: Run `obsidian` with no args for interactive terminal with autocomplete

---

## General

| Command | Description |
|---------|-------------|
| `help` | Display available commands or help for a specific command |
| `version` | Show Obsidian version |
| `reload` | Reload app window (dangerous) |
| `restart` | Restart application (dangerous) |

## Vault

| Command | Description |
|---------|-------------|
| `vault` | Show current vault information |
| `vaults` | List all known vaults (desktop only) |

## Files and Folders

| Command | Description |
|---------|-------------|
| `file` | Show file info (defaults to active file) |
| `files` | List vault files. Params: `sort=modified\|created\|name`, `limit=N` |
| `folder` | Show folder information |
| `folders` | List vault folders |
| `open` | Open a file. Params: `file=`, `path=` |
| `create` | Create or overwrite a file. Params: `name=`, `content=`, `template=`. Flags: `silent`, `overwrite` |
| `read` | Read file contents (defaults to active file). Params: `file=`, `path=` |
| `append` | Append content to file (defaults to active). Params: `file=`, `content=` |
| `prepend` | Prepend content after frontmatter (defaults to active). Params: `file=`, `content=` |
| `move` | Move or rename file (defaults to active). Params: `file=`, `to=` |
| `rename` | Rename a file (defaults to active). Params: `file=`, `name=` |
| `delete` | Delete file to trash (defaults to active). Params: `file=` |

## Outline

| Command | Description |
|---------|-------------|
| `outline` | Display headings for current file |

## Search

| Command | Description |
|---------|-------------|
| `search` | Search vault, return matching paths. Params: `query=`, `limit=`, `format=json` |
| `search:context` | Search with line context (grep-style). Params: `query=`, `limit=` |
| `search:open` | Open search view in Obsidian UI |

## Links

| Command | Description |
|---------|-------------|
| `links` | List outgoing links (defaults to active file) |
| `backlinks` | List incoming links (defaults to active file) |
| `unresolved` | List all unresolved links in vault |
| `orphans` | List files with no incoming links |
| `deadends` | List files with no outgoing links |

## Tags

| Command | Description |
|---------|-------------|
| `tags` | List all vault tags. Params: `sort=count\|name`. Flags: `counts` |
| `tag` | Get information about a specific tag. Params: `name=` |

## Tasks

| Command | Description |
|---------|-------------|
| `tasks` | List vault tasks. Params: `file=`, `limit=`. Flags: `todo`, `done`, `daily` |
| `task` | Show or update a specific task |

## Properties (Frontmatter)

| Command | Description |
|---------|-------------|
| `aliases` | List all vault aliases |
| `properties` | List all vault properties |
| `property:read` | Read property value (defaults to active file). Params: `name=`, `file=` |
| `property:set` | Set property value (defaults to active file). Params: `name=`, `value=`, `file=` |
| `property:remove` | Remove property (defaults to active file). Params: `name=`, `file=` |

## Daily Notes

| Command | Description |
|---------|-------------|
| `daily` | Open today's daily note |
| `daily:path` | Get daily note file path |
| `daily:read` | Read daily note contents |
| `daily:append` | Append content to daily note. Params: `content=` |
| `daily:prepend` | Prepend content to daily note. Params: `content=` |

## Random Notes

| Command | Description |
|---------|-------------|
| `random` | Open a random note |
| `random:read` | Read a random note with path |

## Word Count

| Command | Description |
|---------|-------------|
| `wordcount` | Count words/characters (defaults to active file). Params: `file=` |

## Templates

| Command | Description |
|---------|-------------|
| `templates` | List available templates |
| `template:read` | Read template content. Params: `name=` |
| `template:insert` | Insert template into active file. Params: `name=` |

## Bookmarks

| Command | Description |
|---------|-------------|
| `bookmarks` | List all bookmarks |
| `bookmark` | Add a bookmark. Params: `file=` |

## Bases (Databases)

| Command | Description |
|---------|-------------|
| `bases` | List all base files |
| `base:views` | List views in current base |
| `base:query` | Query base and return results |
| `base:create` | Create new base item |

## Commands (Obsidian Internal)

| Command | Description |
|---------|-------------|
| `commands` | List all available Obsidian command IDs |
| `command` | Execute an Obsidian command by ID (dangerous). Params: `id=` |

## Hotkeys

| Command | Description |
|---------|-------------|
| `hotkeys` | List hotkeys for all commands |
| `hotkey` | Get hotkey for a specific command. Params: `id=` |

## Tabs and Workspaces

| Command | Description |
|---------|-------------|
| `tabs` | List open tabs |
| `tab:open` | Open a new tab |
| `recents` | List recently opened files |
| `workspace` | Show workspace tree |
| `workspaces` | List saved workspaces |
| `workspace:save` | Save current layout as workspace. Params: `name=` |
| `workspace:load` | Load saved workspace. Params: `name=` |
| `workspace:delete` | Delete saved workspace. Params: `name=` |

## Web Viewer

| Command | Description |
|---------|-------------|
| `web` | Open URL in web viewer. Params: `url=` |

## Plugins

| Command | Description |
|---------|-------------|
| `plugins` | List installed plugins |
| `plugins:enabled` | List enabled plugins |
| `plugins:restrict` | Toggle restricted mode (dangerous) |
| `plugin` | Get plugin information. Params: `id=` |
| `plugin:enable` | Enable a plugin. Params: `id=` |
| `plugin:disable` | Disable a plugin. Params: `id=` |
| `plugin:install` | Install community plugin. Params: `id=` |
| `plugin:uninstall` | Uninstall a plugin. Params: `id=` |
| `plugin:reload` | Reload a plugin (for dev). Params: `id=` |

## Themes

| Command | Description |
|---------|-------------|
| `themes` | List installed themes |
| `theme` | Show active theme or get theme info |
| `theme:set` | Set active theme. Params: `name=` |
| `theme:install` | Install community theme. Params: `name=` |
| `theme:uninstall` | Uninstall a theme. Params: `name=` |

## CSS Snippets

| Command | Description |
|---------|-------------|
| `snippets` | List CSS snippets |
| `snippets:enabled` | List enabled snippets |
| `snippet:enable` | Enable a snippet. Params: `name=` |
| `snippet:disable` | Disable a snippet. Params: `name=` |

## File History (Recovery)

| Command | Description |
|---------|-------------|
| `diff` | List/compare file versions from recovery and Sync |
| `history` | List versions from file recovery |
| `history:list` | List files with local history |
| `history:read` | Read a local history version |
| `history:restore` | Restore a local history version |
| `history:open` | Open file recovery UI |

## Sync

| Command | Description |
|---------|-------------|
| `sync` | Pause or resume Obsidian Sync |
| `sync:status` | Show sync status and usage |
| `sync:history` | List sync version history (defaults to active file) |
| `sync:read` | Read sync version (defaults to active file) |
| `sync:restore` | Restore sync version (defaults to active file) |
| `sync:open` | Open sync history UI (defaults to active file) |
| `sync:deleted` | List deleted files in sync |

## Publish

| Command | Description |
|---------|-------------|
| `publish:site` | Show publish site information |
| `publish:list` | List published files |
| `publish:status` | List publish changes |
| `publish:add` | Publish a file (defaults to active file) |
| `publish:remove` | Unpublish a file (defaults to active file) |
| `publish:open` | Open published file in browser (defaults to active file) |

## Developer Commands

| Command | Description |
|---------|-------------|
| `devtools` | Toggle Electron DevTools |
| `eval` | Execute JavaScript and return result. Params: `code=` |
| `dev:console` | Show captured console messages. Params: `level=error\|warn\|log\|debug` |
| `dev:errors` | Show captured JavaScript errors |
| `dev:screenshot` | Take screenshot (base64 PNG). Params: `path=`, `file=` |
| `dev:dom` | Query DOM elements. Params: `selector=`. Flags: `text` |
| `dev:css` | Inspect CSS with source locations. Params: `selector=`, `prop=` |
| `dev:mobile` | Toggle mobile emulation. Params: `on\|off` |
| `dev:debug` | Attach/detach Chrome DevTools Protocol debugger |
| `dev:cdp` | Run Chrome DevTools Protocol command |

---

## Headless Sync (Linux Server)

Run Obsidian Sync without GUI for server automation:

```bash
obsidian sync --vault="path/to/vault"
```

## Search Operators (in search query=)

| Operator | Example | Purpose |
|----------|---------|---------|
| `file:` | `file:meeting` | Filter by filename |
| `path:` | `path:projects/` | Filter by path |
| `content:` | `content:TODO` | Search in content only |
| `tag:` | `tag:#important` | Filter by tag |
| `task:` | `task:` | Find tasks |
| `task-todo:` | `task-todo:` | Find incomplete tasks |
| `task-done:` | `task-done:` | Find completed tasks |
| `line:` | `line:(foo bar)` | Both terms on same line |
| `section:` | `section:(heading text)` | Search within sections |
| `block:` | `block:(term)` | Search within blocks |

## Windows Setup

The `obsidian` command is added to PATH during installation. If not found:

```bash
# Default location
"C:\Users\<user>\AppData\Local\Obsidian\obsidian.exe"

# Or add to PATH
export PATH="$PATH:/c/Users/<user>/AppData/Local/Obsidian"
```
