# Obsidian CLI — Working Examples

> Practical workflows for note-taking, productivity, development, and automation.

**Reference:** [references/obsidian-cli.md](../references/obsidian-cli.md)

---

## Daily Note Workflows

### Open Today's Daily Note

```bash
obsidian daily
```

### Read Today's Daily Note Content

```bash
obsidian daily:read
```

### Add Task to Daily Note

```bash
obsidian daily:append content="- [ ] Review pull requests"
```

### Add Multiple Items to Daily Note

```bash
obsidian daily:append content="## Meeting Notes\n- Discussed Q2 roadmap\n- Action items:\n\t- [ ] Update sprint board\n\t- [ ] Schedule follow-up"
```

### Prepend Summary to Daily Note

```bash
obsidian daily:prepend content="## Day Summary\nCompleted 5 tasks, 2 meetings."
```

### Get Daily Note Path (for scripting)

```bash
obsidian daily:path
```

---

## Note Creation & Editing

### Create a New Note

```bash
obsidian create name="Meeting Notes 2026-04-04" content="# Meeting Notes\n\n## Attendees\n\n## Agenda\n\n## Action Items"
```

### Create from Template (without opening)

```bash
obsidian create name="Weekly Review" template="Weekly Review Template" silent
```

### Create and Overwrite Existing

```bash
obsidian create name="Status Report" content="# Status Report\nUpdated content" overwrite
```

### Read a Note

```bash
obsidian read file="Project Plan"
```

### Read by Exact Path

```bash
obsidian read path="projects/routemagic/architecture.md"
```

### Append to a Note

```bash
obsidian append file="Running Log" content="\n## April 4, 2026\n- 5km in 25:30"
```

### Prepend to a Note (after frontmatter)

```bash
obsidian prepend file="Inbox" content="- [ ] New idea: CLI automation pipeline"
```

### Move/Rename a Note

```bash
obsidian move file="Draft Notes" to="archive/Draft Notes"
obsidian rename file="Old Name" name="New Name"
```

### Delete a Note (to trash)

```bash
obsidian delete file="Scratch Pad"
```

---

## Search & Discovery

### Search Vault

```bash
obsidian search query="API endpoint"
```

### Search with Limit and JSON Output

```bash
obsidian search query="deployment" limit=5 format=json
```

### Search with Context (grep-style)

```bash
obsidian search:context query="TODO" limit=20
```

### Search with Operators

```bash
# Search in specific folder
obsidian search query="path:projects/ deployment"

# Search by tag
obsidian search query="tag:#urgent"

# Find incomplete tasks
obsidian search query="task-todo:"

# Find tasks on same line as keyword
obsidian search query="line:(deadline April)"
```

### Copy Search Results to Clipboard

```bash
obsidian search query="meeting notes" --copy
```

### Find Unresolved Links

```bash
obsidian unresolved
```

### Find Orphan Notes (no incoming links)

```bash
obsidian orphans
```

### Find Dead-End Notes (no outgoing links)

```bash
obsidian deadends
```

### List Backlinks for a Note

```bash
obsidian backlinks file="Project Plan"
```

### List Outgoing Links

```bash
obsidian links file="Project Plan"
```

---

## Task Management

### List All Tasks from Daily Note

```bash
obsidian tasks daily
```

### List Incomplete Tasks

```bash
obsidian tasks todo
```

### List Completed Tasks

```bash
obsidian tasks done
```

### List Tasks from Specific File

```bash
obsidian tasks file="Sprint Board"
```

### List Tasks with Limit

```bash
obsidian tasks todo limit=10
```

---

## Tags & Properties

### List All Tags with Counts

```bash
obsidian tags counts sort=count
```

### Get Tag Info

```bash
obsidian tag name="project"
```

### Read a Property from a Note

```bash
obsidian property:read name="status" file="Feature Spec"
```

### Set a Property

```bash
obsidian property:set name="status" value="in-progress" file="Feature Spec"
```

### Set Multiple Properties

```bash
obsidian property:set name="priority" value="high" file="Bug Report"
obsidian property:set name="assignee" value="prith" file="Bug Report"
```

### Remove a Property

```bash
obsidian property:remove name="draft" file="Published Article"
```

### List All Vault Properties

```bash
obsidian properties
```

### List All Aliases

```bash
obsidian aliases
```

---

## File Management

### List Recently Modified Files

```bash
obsidian files sort=modified limit=10
```

### List Recently Created Files

```bash
obsidian files sort=created limit=5
```

### Copy File List to Clipboard

```bash
obsidian files sort=modified limit=20 --copy
```

### Get File Info

```bash
obsidian file file="Project Plan"
```

### List Folders

```bash
obsidian folders
```

### Get Word Count

```bash
obsidian wordcount file="Blog Post"
```

### Get Note Outline (Headings)

```bash
obsidian outline file="Architecture Doc"
```

---

## Templates

### List Available Templates

```bash
obsidian templates
```

### Read a Template

```bash
obsidian template:read name="Meeting Notes"
```

### Insert Template into Active File

```bash
obsidian template:insert name="Daily Review"
```

---

## Bookmarks & Recents

### List Bookmarks

```bash
obsidian bookmarks
```

### Add Bookmark

```bash
obsidian bookmark file="Important Reference"
```

### List Recently Opened Files

```bash
obsidian recents
```

---

## Workspace Management

### Save Current Workspace

```bash
obsidian workspace:save name="coding-layout"
```

### Load a Workspace

```bash
obsidian workspace:load name="writing-layout"
```

### List Saved Workspaces

```bash
obsidian workspaces
```

### Show Current Workspace Tree

```bash
obsidian workspace
```

---

## Plugin Management

### List Installed Plugins

```bash
obsidian plugins
```

### List Enabled Plugins

```bash
obsidian plugins:enabled
```

### Install a Community Plugin

```bash
obsidian plugin:install id="dataview"
```

### Enable/Disable Plugin

```bash
obsidian plugin:enable id="calendar"
obsidian plugin:disable id="calendar"
```

### Reload Plugin (Development)

```bash
obsidian plugin:reload id="my-plugin"
```

### Get Plugin Info

```bash
obsidian plugin id="dataview"
```

---

## Theme & Appearance

### Set Theme

```bash
obsidian theme:set name="Minimal"
```

### Install Community Theme

```bash
obsidian theme:install name="Prism"
```

### List/Enable/Disable CSS Snippets

```bash
obsidian snippets
obsidian snippet:enable name="custom-colors"
obsidian snippet:disable name="custom-colors"
```

---

## Developer & Debugging

### Take Screenshot of Obsidian Window

```bash
obsidian dev:screenshot path="/tmp/obsidian-screenshot.png"
```

### Execute JavaScript

```bash
# Count files in vault
obsidian eval code="app.vault.getFiles().length"

# Get vault name
obsidian eval code="app.vault.getName()"

# List all markdown files
obsidian eval code="app.vault.getMarkdownFiles().map(f => f.path).join('\n')"

# Get active file path
obsidian eval code="app.workspace.getActiveFile()?.path"
```

### Check Console Errors

```bash
obsidian dev:errors
```

### Filter Console Messages

```bash
obsidian dev:console level=error
obsidian dev:console level=warn
```

### Inspect DOM Elements

```bash
obsidian dev:dom selector=".workspace-leaf" text
obsidian dev:dom selector=".nav-file-title"
```

### Inspect CSS

```bash
obsidian dev:css selector=".workspace-leaf" prop=background-color
```

### Toggle Mobile Emulation

```bash
obsidian dev:mobile on
obsidian dev:mobile off
```

### Open DevTools

```bash
obsidian devtools
```

### Run CDP Command

```bash
obsidian dev:cdp method="Page.captureScreenshot" params='{"format":"png"}'
```

---

## Sync Operations

### Check Sync Status

```bash
obsidian sync:status
```

### Pause/Resume Sync

```bash
obsidian sync pause
obsidian sync resume
```

### View Sync History for a File

```bash
obsidian sync:history file="Project Plan"
```

### Restore a Sync Version

```bash
obsidian sync:restore file="Project Plan"
```

### List Deleted Files in Sync

```bash
obsidian sync:deleted
```

---

## File History & Recovery

### View File Versions

```bash
obsidian diff file="Important Doc"
```

### List Files with Local History

```bash
obsidian history:list
```

### Restore a Local History Version

```bash
obsidian history:restore file="Accidentally Edited"
```

---

## Publish

### List Published Files

```bash
obsidian publish:list
```

### Check Publish Status (changed files)

```bash
obsidian publish:status
```

### Publish/Unpublish a File

```bash
obsidian publish:add file="Blog Post"
obsidian publish:remove file="Draft Post"
```

---

## Multi-Vault Operations

### Target a Specific Vault

```bash
obsidian vault="Work Vault" search query="meeting"
obsidian vault="Personal" daily:read
obsidian vault="Work Vault" files sort=modified limit=5
```

### List All Vaults

```bash
obsidian vaults
```

---

## Automation Patterns

### Morning Standup Script

```bash
# Read yesterday's tasks, add today's daily note with template
obsidian daily
obsidian daily:append content="## Standup\n### Yesterday\n- \n### Today\n- \n### Blockers\n- "
```

### End-of-Day Review

```bash
# Check what was done
obsidian tasks done daily
obsidian daily:append content="\n## End of Day Review\nCompleted $(obsidian tasks done daily total) tasks."
```

### Quick Capture Inbox Item

```bash
obsidian append file="Inbox" content="- [ ] $(date +%H:%M) Quick thought or task"
```

### Weekly Report Pipeline

```bash
# Create weekly report from template
obsidian create name="Weekly Report $(date +%Y-%m-%d)" template="Weekly Report" silent

# Search for completed tasks this week
obsidian search query="task-done:" format=json --copy
```

### Plugin Development Cycle

```bash
# 1. Make code changes externally
# 2. Reload plugin
obsidian plugin:reload id="my-plugin"
# 3. Check for errors
obsidian dev:errors
# 4. Screenshot to verify UI
obsidian dev:screenshot path="/tmp/plugin-test.png"
# 5. Inspect specific element
obsidian dev:dom selector=".my-plugin-view" text
# 6. Check console
obsidian dev:console level=error
```

### Bases (Database) Query

```bash
obsidian base:query query="status = 'active'" format=json
obsidian base:create type="task" title="New Item" status="todo"
```
