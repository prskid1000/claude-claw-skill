# Knowledge Base — Obsidian System

> Persistent, structured knowledge mesh using Obsidian MCP. Dense nodes, not session dumps.

**Related:** [issue-tracker.md](issue-tracker.md) | [pipelines.md](pipelines.md) | [bootstrap.md](bootstrap.md)

---

## Vault Structure

```
Claude/
├── KB/
│   ├── _index.md                # Root index → links to all branches
│   ├── Projects/{Name}/
│   │   ├── _index.md            # Project overview
│   │   ├── Architecture.md      # System design, tech stack
│   │   ├── Entities.md          # Domain models, schemas
│   │   ├── Patterns.md          # Conventions & patterns
│   │   ├── APIs.md              # Endpoints, services
│   │   ├── Bugs.md              # Known issues, gotchas
│   │   └── {Topic}.md           # Other dense topic nodes
│   ├── Patterns/                # Cross-project patterns
│   ├── Decisions/               # ADR-style: {YYYY-MM-DD}-{slug}.md
│   └── People/                  # Team roles, preferences
├── Board/                       # → see issue-tracker.md
├── WorkLog/{YYYY-MM}.md         # Append-only monthly log
└── Research/                    # Deep-dive notes
```

## Read Before Act (Non-Negotiable)

Before ANY work:
1. `search_notes` with project/topic keywords
2. `read_multiple_notes` for project index + WorkLog + Board
3. On error → search `Bugs.md` for similar past errors
4. New conversation → scan recent sessions for continuity

## Node Rules

| Rule | Details |
|------|---------|
| Patch, don't replace | `patch_note` for sections, `write_note(mode=append)` for WorkLog |
| Dense, not verbose | Tables, bullets, code blocks. No prose paragraphs |
| Atomic nodes | One concept per file. Split at 2+ topics |
| Link densely | Min 2 `[[wikilinks]]` per update. Mesh > tree |
| Frontmatter required | `type: kb\|worklog\|decision\|research`, `project`, `updated` |
| Bug status required | `investigating \| root-caused \| resolved \| wont-fix` |
| Tag entities | `tags: [entity-name, module-name]` in frontmatter |
| No blank nodes | Never create placeholder/empty content |

### KB Node Frontmatter

```yaml
---
type: kb
project: ProjectName
updated: 2026-03-25
tags: [module-name, entity-name]
---
```

## Data Hygiene

| Action | When |
|--------|------|
| Truncate old WorkLog | >3 months → compress to monthly summary |
| Merge duplicates | Overlapping nodes → merge, redirect `[[moved to X]]` |
| Bidirectional links | A→B → also patch B→A |
| Prune stale bugs | Resolved >1 month → Resolved Archive section |
| Densify on revisit | Verbose prose → tables, redundant → merged |
| Update indexes | Node create/remove → update parent `_index.md` |

## Subagent Prompt Template

```
You are the Cortex KB updater. You have Obsidian MCP tools.

TRIGGER: {trigger name}
CONTEXT: {brief context}

RULES:
- Read target node FIRST (avoid overwriting)
- patch_note for existing, write_note(mode=append) for WorkLog
- Dense: tables, bullets, code blocks. No fluff
- Never create blank/placeholder nodes
- Frontmatter: current date + relevant tags
- [[wikilinks]]: min 2, bidirectional
- Board tickets: update both ticket AND _board.md
- Auto-increment IDs via _counter.md
- HOUSEKEEPING: truncate, merge, densify, archive

NODES TO UPDATE:
- {list nodes}

CONTENT:
{knowledge to persist}
```

## WorkLog Entry Format

```markdown
### {HH:MM} — {brief title} [{trigger}]
- **Did:** {what was accomplished}
- **Files:** `path/to/file.java`, `path/to/other.ts`
- **Tickets:** [[TASK-NNN]], [[BUG-NNN]]
- **Decisions:** {choices made and why}
- **Errors:** {errors + resolution, or "none"}
- **Learned:** {new knowledge, if any}
- **Next:** {what's pending}
- **Links:** [[KB/Projects/X/Topic]], [[KB/Decisions/...]]
```

## Bug Entry Format

```markdown
#### {date} — {error title}
- **Status:** `investigating` | `root-caused` | `resolved`
- **Error:** `{error message}`
- **Context:** {what was happening}
- **Debug trail:**
  - {HH:MM} Hypothesis: {theory}
  - {HH:MM} Tested: {attempt}
  - {HH:MM} Result: {outcome}
- **Root cause:** {why}
- **Fix:** {change} → `{file:line}`
- **Prevention:** {how to avoid}
- **Links:** [[Patterns]], [[Decisions/...]]
```

## MCP Tools — Complete Reference

### Core CRUD

| Tool | Signature | Purpose |
|------|-----------|---------|
| `write_note` | `(path, content, frontmatter?, mode=overwrite\|append\|prepend)` | Create or update a note |
| `read_note` | `(path, prettyPrint=false)` | Read single note |
| `read_multiple_notes` | `(paths[], includeContent=true, includeFrontmatter=true)` | Batch read up to 10 notes |
| `patch_note` | `(path, oldString, newString, replaceAll=false)` | Surgical text replacement |
| `delete_note` | `(path, confirmPath)` | Delete (confirmPath must match path) |

### Search & Discovery

| Tool | Signature | Purpose |
|------|-----------|---------|
| `search_notes` | `(query, limit=5, searchContent=true, searchFrontmatter=false)` | Search by content or frontmatter |
| `list_directory` | `(path="/")` | List files/folders in vault |
| `get_vault_stats` | `(recentCount=5)` | Vault overview: totals, size, recent files |

### Metadata

| Tool | Signature | Purpose |
|------|-----------|---------|
| `get_frontmatter` | `(path)` | Read only frontmatter (fast) |
| `get_notes_info` | `(paths[])` | Metadata for multiple notes without content |
| `update_frontmatter` | `(path, frontmatter, merge=true)` | Update frontmatter only |
| `manage_tags` | `(path, operation=add\|remove\|list, tags[]?)` | Tag management |

### Move & Organize

| Tool | Signature | Purpose |
|------|-----------|---------|
| `move_note` | `(oldPath, newPath, overwrite=false)` | Move/rename a note |
| `move_file` | `(oldPath, newPath, confirmOldPath, confirmNewPath)` | Move any file (binary-safe) |

### Usage Patterns

```python
# Session start — bulk context load
read_multiple_notes(["KB/Projects/RM/_index.md", "WorkLog/2026-03.md", "Board/_board.md"])

# Quick metadata scan
get_notes_info(["Board/Tasks/TASK-001.md", "Board/Tasks/TASK-002.md"])

# Vault overview
get_vault_stats(recentCount=10)

# Find all P0 bugs via frontmatter
search_notes("P0", searchContent=False, searchFrontmatter=True, limit=20)
```
