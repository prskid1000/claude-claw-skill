# Obsidian CLI — Working Examples

> Practical workflows for note-taking, productivity, development, and automation.

**Reference:** [references/obsidian-cli.md](../references/obsidian-cli.md)

---

## Daily Note Workflows

```bash
# Open today's daily note
obsidian daily

# Read daily note content
obsidian daily:read

# Add a task to daily note
obsidian daily:append content="- [ ] Review pull requests"

# Add structured meeting notes
obsidian daily:append content="## Meeting Notes\n- Discussed Q2 roadmap\n- Action items:\n\t- [ ] Update sprint board\n\t- [ ] Schedule follow-up"

# Prepend priority section
obsidian daily:prepend content="## Priority\n- Ship feature X by EOD"
```

## Note Creation & Editing

```bash
# Create a new note with content
obsidian create name="Meeting Notes 2026-04-04" content="# Meeting\n\n## Attendees\n\n## Agenda\n\n## Action Items"

# Create from template without opening
obsidian create name="Weekly Review" template="Weekly Review Template" silent

# Create and overwrite existing
obsidian create name="Status Report" content="# Updated Report" overwrite

# Read a note by name
obsidian read file="Project Plan"

# Read by exact path
obsidian read path="projects/routemagic/architecture.md"

# Append to a running log
obsidian append file="Running Log" content="\n## April 4, 2026\n- 5km in 25:30"

# Prepend to inbox (after frontmatter)
obsidian prepend file="Inbox" content="- [ ] New idea: CLI automation pipeline"

# Move note to archive
obsidian move file="Draft Notes" to="archive/Draft Notes"

# Delete to trash
obsidian delete file="Scratch Pad"
```

## Search & Discovery

```bash
# Basic search
obsidian search query="API endpoint"

# Search with limit and JSON output
obsidian search query="deployment" limit=5 format=json

# Search with context (grep-style, shows surrounding lines)
obsidian search:context query="TODO" limit=10

# Search in specific folder
obsidian search query="path:projects/ deployment"

# Search by tag
obsidian search query="tag:#urgent"

# Find all incomplete tasks
obsidian search query="task-todo:"

# Find backlinks to a note
obsidian backlinks file="Project Plan"

# Find unresolved (broken) links
obsidian unresolved

# List 10 most recently modified files
obsidian files sort=modified limit=10
```

## Task Management

```bash
# List all incomplete tasks
obsidian tasks todo

# List tasks from daily note only
obsidian tasks daily todo

# List completed tasks
obsidian tasks done

# Tasks from a specific file
obsidian tasks file="Sprint Board" todo limit=10

# Count of incomplete tasks
obsidian tasks todo total
```

## Tags & Properties

```bash
# List all tags sorted by frequency
obsidian tags counts sort=count

# Read a property from a note
obsidian property:read name="status" file="Feature Spec"

# Set a property
obsidian property:set name="status" value="done" file="Feature Spec"
obsidian property:set name="priority" value="high" file="Bug Report"

# Remove a property
obsidian property:remove name="draft" file="Published Article"
```

## Templates

```bash
# List available templates
obsidian templates

# Insert template into active file
obsidian template:insert name="Meeting Notes"
```

## Developer & Debugging

```bash
# Take screenshot of Obsidian window
obsidian dev:screenshot path="/tmp/obsidian-screenshot.png"

# Execute JavaScript (access Obsidian app API)
obsidian eval code="app.vault.getFiles().length"
obsidian eval code="app.vault.getName()"
obsidian eval code="app.workspace.getActiveFile()?.path"

# Check for errors
obsidian dev:errors

# Filter console messages
obsidian dev:console level=error

# Inspect DOM element
obsidian dev:dom selector=".workspace-leaf" text

# Inspect CSS property
obsidian dev:css selector=".workspace-leaf" prop=background-color

# Reload a plugin (development)
obsidian plugin:reload id="my-plugin"
```

## Workspace Management

```bash
# Save current layout
obsidian workspace:save name="coding-layout"

# Restore a saved layout
obsidian workspace:load name="writing-layout"

# List saved workspaces
obsidian workspaces
```

## Multi-Vault

```bash
# Target a specific vault
obsidian vault="Work" search query="meeting"
obsidian vault="Personal" daily:read

# List all known vaults
obsidian vaults
```

## Automation Patterns

### Morning Standup
```bash
obsidian daily
obsidian daily:append content="## Standup\n### Yesterday\n- \n### Today\n- \n### Blockers\n- "
```

### Quick Capture to Inbox
```bash
obsidian append file="Inbox" content="- [ ] Quick thought or task"
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
# 5. Check console
obsidian dev:console level=error
```
